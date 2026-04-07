

import lmstudio as lms
import requests
import ollama
import os
import time
import asyncio
import heapq
import threading
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Any, Dict, List
from dotenv import load_dotenv
from openai import OpenAI
from google import genai
from google.genai import types
from huggingface_hub import InferenceClient
from pydantic import ValidationError, BaseModel

load_dotenv()

# Configuración de conexión al servidor remoto
BASE_URL_LM = os.getenv("BASE_URL_LM", "http://localhost:1234/v1")
OPENAI_KEY = os.getenv("OPENAI_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configuración específica para Ollama en VM
OLLAMA_VM_URL = os.getenv("OLLAMA_VM_URL", "http://localhost:11434")  # Usa localhost por el túnel SSH
OLLAMA_VM_MODEL = os.getenv("OLLAMA_VM_MODEL", "qwen3.5:9b")
USE_SSH_TUNNEL = os.getenv("USE_SSH_TUNNEL", "true").lower() == "true"

class Priority(Enum):
    URGENTE = 0    # Prioridad más alta
    ALTA = 1
    MEDIA = 2
    BAJA = 3       # Prioridad más baja
    BATCH = 4      # Para procesamiento por lotes

@dataclass
class QueuedRequest:
    priority: Priority
    prompt: str
    request_id: str
    timestamp: float
    model: str
    system_prompt: Optional[str] = None
    temperature: float = 0.2
    response_format: Optional[BaseModel] = None
    callback: Optional[callable] = None
    future: Optional[asyncio.Future] = None
    
    def __lt__(self, other):
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        return self.timestamp < other.timestamp

class OllamaVMClient:
    """Cliente especializado para conectarse a Ollama en VM vía túnel SSH"""
    
    def __init__(self, base_url: str = OLLAMA_VM_URL, model: str = OLLAMA_VM_MODEL):
        self.base_url = base_url
        self.model = model
        self.client = ollama.Client(host=base_url)  # Cliente síncrono
        self.async_client = ollama.AsyncClient(host=base_url)
        
    def generate(self, prompt: str, **kwargs):
        """Genera respuesta usando el modelo en VM"""
        options = {
            "temperature": kwargs.get("temperature", 0.2),
            "num_predict": kwargs.get("max_tokens", 512),
        }
        
        response = self.client.generate(
            model=self.model,
            prompt=prompt,
            options=options
        )
        return response['response']
    
    async def generate_async(self, prompt: str, **kwargs):
        """Versión asíncrona para la cola de prioridad"""
        options = {
            "temperature": kwargs.get("temperature", 0.2),
            "num_predict": kwargs.get("max_tokens", 512),
        }
        
        response = await self.async_client.generate(
            model=self.model,
            prompt=prompt,
            options=options
        )
        return response['response']
    
    def list_models(self):
        """Lista los modelos disponibles en la VM"""
        return self.client.list()
    
    def show_model_info(self):
        """Muestra información del modelo"""
        return self.client.show(self.model)
    
    def check_connection(self):
        """Verifica que la conexión a la VM funcione"""
        try:
            self.client.list()
            return True, "Conexión exitosa a Ollama VM"
        except Exception as e:
            return False, f"Error de conexión: {e}"

class PriorityQueueLLM:
    """Cola de prioridad para manejar requests a LLM"""
    
    def __init__(self, max_workers: int = 4, ollama_vm_config: Optional[Dict] = None):
        self.max_workers = max_workers
        self.queue = []  # Min-heap
        self.active_requests = 0
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.running = True
        self.stats = {
            "total_processed": 0,
            "by_priority": {p.name: 0 for p in Priority},
            "avg_wait_time": 0,
            "total_wait_time": 0
        }
        
        # Inicializar clientes
        self.ollama_vm = OllamaVMClient(
            base_url=ollama_vm_config.get("base_url", OLLAMA_VM_URL) if ollama_vm_config else OLLAMA_VM_URL,
            model=ollama_vm_config.get("model", OLLAMA_VM_MODEL) if ollama_vm_config else OLLAMA_VM_MODEL
        )
        
        # Verificar conexión al inicio
        success, message = self.ollama_vm.check_connection()
        if not success:
            print(f"Advertencia: {message}")
            print("   Asegúrate de que el túnel SSH esté activo: ssh -N ollama-server")
        else:
            print(f"{message}")
        
        # Iniciar workers
        self.workers = []
        for i in range(max_workers):
            worker = threading.Thread(target=self._worker_loop, name=f"LLM-Worker-{i}")
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
    
    def add_request(self, 
                   prompt: str, 
                   priority: Priority = Priority.MEDIA,
                   model: Optional[str] = None,
                   system_prompt: Optional[str] = None,
                   temperature: float = 0.2,
                   response_format: Optional[BaseModel] = None,
                   request_id: Optional[str] = None,
                   callback: Optional[callable] = None) -> str:
        """Añade una request a la cola con prioridad"""
        
        with self.lock:
            req_id = request_id or f"req_{int(time.time()*1000)}_{len(self.queue)}"
            
            # Construir prompt completo si hay system_prompt
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            
            request = QueuedRequest(
                priority=priority,
                prompt=full_prompt,
                request_id=req_id,
                timestamp=time.time(),
                model=model or self.ollama_vm.model,
                temperature=temperature,
                response_format=response_format,
                callback=callback
            )
            
            heapq.heappush(self.queue, request)
            print(f"📥 [{priority.name}] Request {req_id} encolada")
            self.condition.notify()
            
            return req_id
    
    def add_batch(self, 
                  prompts: List[str], 
                  priority: Priority = Priority.BATCH,
                  **kwargs) -> List[str]:
        """Añade múltiples requests (batch) con la misma prioridad"""
        request_ids = []
        for i, prompt in enumerate(prompts):
            req_id = self.add_request(
                prompt=prompt,
                priority=priority,
                request_id=f"batch_{int(time.time())}_{i}",
                **kwargs
            )
            request_ids.append(req_id)
        return request_ids
    
    def _worker_loop(self):
        """Worker que procesa requests de la cola"""
        while self.running:
            request = None
            wait_time = 0
            
            with self.lock:
                # Esperar hasta que haya requests
                while len(self.queue) == 0 and self.running:
                    self.condition.wait()
                
                if not self.running:
                    break
                
                request = heapq.heappop(self.queue)
                self.active_requests += 1
                wait_time = time.time() - request.timestamp
            
            if request:
                # Procesar request
                start_time = time.time()
                try:
                    # Usar el cliente de Ollama VM
                    response = self.ollama_vm.generate(
                        prompt=request.prompt,
                        temperature=request.temperature
                    )
                    
                    elapsed = time.time() - start_time
                    
                    with self.lock:
                        self.stats["total_processed"] += 1
                        self.stats["by_priority"][request.priority.name] += 1
                        self.stats["total_wait_time"] += wait_time
                        self.stats["avg_wait_time"] = (
                            self.stats["total_wait_time"] / self.stats["total_processed"]
                        )
                    
                    print(f"✅ [{request.priority.name}] Request {request.request_id}: "
                          f"{elapsed:.2f}s (espera: {wait_time:.2f}s)")
                    
                    if request.callback:
                        request.callback(response)
                        
                except Exception as e:
                    print(f"❌ Error procesando {request.request_id}: {e}")
                
                finally:
                    with self.lock:
                        self.active_requests -= 1
    
    def get_status(self) -> Dict:
        """Obtiene estado actual de la cola"""
        with self.lock:
            return {
                "queue_size": len(self.queue),
                "active_requests": self.active_requests,
                "max_workers": self.max_workers,
                "pending_priorities": [r.priority.name for r in self.queue[:5]],
                "stats": self.stats.copy(),
                "connected_to_vm": self.ollama_vm.check_connection()[0]
            }
    
    def shutdown(self):
        """Apaga la cola de prioridad"""
        self.running = False
        with self.condition:
            self.condition.notify_all()

class LLMClient:
    def __init__(self, model_name, provider="lmstudio", base_url=BASE_URL_LM, api_key=OPENAI_KEY):
        self.provider = provider.lower()
        self.model_name = model_name
        self.base_url = base_url
        self.api_key = api_key
        self.priority_queue = None
        
        # Si es Ollama y estamos usando VM, inicializar cola de prioridad
        if self.provider == "ollama" and USE_SSH_TUNNEL:
            self.priority_queue = PriorityQueueLLM(
                max_workers=4,  # Ajusta según OLLAMA_NUM_PARALLEL
                ollama_vm_config={
                    "base_url": OLLAMA_VM_URL,
                    "model": self.model_name
                }
            )
        
        self.client = self.init_client()
        self.model = self.init_model()

    def init_client(self):
        if self.provider == "openai":
            return OpenAI(api_key=self.api_key)
        
        elif self.provider == "lmstudio":
            print(self.base_url)
            return lms.get_default_client()
        
        elif self.provider == "google":
            return genai.Client(api_key=GEMINI_API_KEY)

        elif self.provider == "huggingface":
            return InferenceClient(model=self.model_name, token=self.api_key)
        
        elif self.provider == "ollama":
            if USE_SSH_TUNNEL:
                # Usar el cliente de VM a través del túnel
                return OllamaVMClient(base_url=OLLAMA_VM_URL, model=self.model_name)
            else:
                # Usa Ollama ignorando la cola, pero APUNTANDO A LA INFO DEL ENV
                # import ollama
                # return ollama.Client(host=OLLAMA_VM_URL)
                return OllamaVMClient(base_url=OLLAMA_VM_URL, model=self.model_name)
        
        else:
            raise ValueError(f"Proveedor de LLM no soportado: {self.provider}")
    
    def init_model(self):
        if self.provider == "lmstudio":
            return self.client.llm.load_new_instance(
                self.model_name,
                config={
                    "contextLength": 16000,
                    "gpu": {"ratio": 0.5}
                }
            )
        return None

    def set_unload_model(self):
        if self.model:
            self.model.unload()

    def call(self, prompt, system_prompt=None, temperature=0.2, response_format=None, priority=Priority.MEDIA):
        """
        Llama al LLM. Para Ollama VM, usa la cola de prioridad.
        """
        # Si es Ollama VM con cola de prioridad
        if self.provider == "ollama" and self.priority_queue:
            # Para calls síncronas con prioridad, necesitamos esperar
            import uuid
            result_container = []
            event = threading.Event()
            
            def callback(response):
                result_container.append(response)
                event.set()
            
            request_id = self.priority_queue.add_request(
                prompt=prompt,
                priority=priority,
                system_prompt=system_prompt,
                temperature=temperature,
                response_format=response_format,
                callback=callback,
                request_id=f"sync_{uuid.uuid4().hex[:8]}"
            )
            
            # Esperar resultado (timeout 60 segundos)
            if event.wait(timeout=60):
                return result_container[0]
            else:
                raise TimeoutError(f"Timeout esperando respuesta para request {request_id}")
        
        # Comportamiento normal para otros proveedores o Ollama sin cola
        elif self.provider == "openai":
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        
        elif self.provider == "lmstudio":
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            lm_config = {"temperature": temperature}
            
            if response_format:
                response = self.model.respond(full_prompt, response_format=response_format, config=lm_config)
                parsed = response.parsed
                try:
                    return response_format.model_validate(parsed)
                except ValidationError as e:
                    print(f"Error de validación ({response_format.__name__}): {e}")
                    raise e
            else:
                response = self.model.respond(full_prompt, config=lm_config)
                if hasattr(response, 'text'): return str(response.text)
                elif hasattr(response, 'content'): return str(response.content)
                else: return str(response)

        elif self.provider == "google":
            if response_format:
                config = types.GenerateContentConfig(
                    response_mime_type="application/json", 
                    response_schema=response_format, 
                    thinking_config=types.ThinkingConfig(thinking_budget=0)
                )
            else:
                config = None
                
            time.sleep(10)
            if config:
                response = self.client.models.generate_content(
                    model=self.model_name, 
                    contents=prompt, 
                    config=config
                )
            else:
                response = self.client.models.generate_content(
                    model=self.model_name, 
                    contents=prompt
                )
            return response.text
    
        elif self.provider == "ollama" and not self.priority_queue:
            # Ollama local sin cola
            full_prompt = f"{system_prompt}\n{prompt}" if system_prompt else prompt
            if isinstance(self.client, OllamaVMClient):
                return self.client.generate(full_prompt, temperature=temperature)
            else:
                response = self.client.generate(self.model_name, full_prompt)
                return response['response']
        
        elif self.provider == "huggingface":
            full_prompt = f"{system_prompt}\n{prompt}" if system_prompt else prompt
            return self.client.text_generation(full_prompt, temperature=temperature, max_new_tokens=512)
    
        else:
            raise NotImplementedError("Proveedor no implementado")
    
    def call_async(self, prompt, priority=Priority.MEDIA, **kwargs):
        """
        Versión asíncrona que no espera respuesta.
        Útil para requests que no necesitan respuesta inmediata.
        """
        if self.provider == "ollama" and self.priority_queue:
            import uuid
            request_id = self.priority_queue.add_request(
                prompt=prompt,
                priority=priority,
                **kwargs,
                request_id=f"async_{uuid.uuid4().hex[:8]}"
            )
            return {"status": "queued", "request_id": request_id}
        else:
            # Para otros proveedores, simplemente llamar sync
            return self.call(prompt, **kwargs)
    
    def get_queue_status(self):
        """Obtiene estado de la cola de prioridad (solo para Ollama VM)"""
        if self.priority_queue:
            return self.priority_queue.get_status()
        return {"message": "Cola de prioridad no disponible para este proveedor"}


if __name__ == "__main__":
    print("🚀 Inicializando cliente LLM con soporte para VM y prioridades")
    print("="*60)
    
    # Verificar túnel SSH
    print("\n🔍 Verificando conexión a VM...")
    print("   Asegúrate de tener el túnel activo: ssh -N ollama-server")
    
    # Inicializar cliente para Ollama en VM
    client = LLMClient(
        model_name="qwen3.5:9b",
        provider="ollama"
    )
    
    # Verificar estado
    status = client.get_queue_status()
    print(f"\n📊 Estado inicial: {status}")
    
    # Ejemplo 1: Request urgente
    print("\n⚡ Enviando request URGENTE...")
    result = client.call(
        "¿Cuál es la capital de Francia?",
        priority=Priority.URGENTE
    )
    print(f"Respuesta: {result}")
    
    # Ejemplo 2: Múltiples requests con diferentes prioridades
    print("\n📨 Enviando múltiples requests con diferentes prioridades...")
    
    # Request de alta prioridad
    client.call_async(
        "Explica la teoría de la relatividad",
        priority=Priority.ALTA,
        system_prompt="Responde de forma concisa"
    )
    
    # Requests batch (baja prioridad)
    for i in range(3):
        client.call_async(
            f"Genera un dato curioso número {i}",
            priority=Priority.BATCH
        )
    
    # Request media prioridad
    client.call_async(
        "¿Qué es el machine learning?",
        priority=Priority.MEDIA
    )
    
    # Monitorear cola
    print("\n📊 Monitoreando cola...")
    for _ in range(5):
        status = client.get_queue_status()
        print(f"  Estado: {status['queue_size']} en cola, "
              f"{status['active_requests']} activos")
        time.sleep(2)
    
    print("\n✅ Ejemplo completado")