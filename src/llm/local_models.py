from crewai import Crew, LLM, Process
from openai import OpenAI
from huggingface_hub import InferenceClient

class LLMClient:
    def __init__(self, model, provider = "llm-studio", base_url=None, api_key=None):
        self.provider = provider.lower()
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        self.client = self.init_client()
        self.llm_crew = self.init_llm_crew()

    def init_client(self):
        if self.provider == "openai":
            
            return OpenAI(api_key=self.api_key)
        
        elif self.provider == "llm-studio":
            return OpenAI(api_key=self.api_key, base_url = self.base_url)
        
        elif self.provider == "huggingface":
            
            return InferenceClient(model=self.model, token=self.api_key)
        
        else:
            raise ValueError(f"Proveedor de LLM no soportado: {self.provider}")

    def call(self, prompt, system_prompt=None, temperature=0.2):
        if self.provider == "openai":
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        
        elif self.provider == "llm-studio":

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            response = response.choices[0].message.content.strip()
            return response if response else "No se encontraron resultados relevantes."

        elif self.provider == "huggingface":
            full_prompt = f"{system_prompt}\n{prompt}" if system_prompt else prompt
            response = self.client.text_generation(full_prompt, temperature=temperature, max_new_tokens=512)
            return response.strip()

        else:
            raise NotImplementedError("Proveedor no implementado")

    def init_llm_crew(self):

        if self.provider == "llm-studio":
            llm = LLM(model="lm_studio/" + self.model, base_url=self.base_url, api_key=self.api_key)
            return llm
        
    def get_llm_crew(self):
        return self.llm_crew
       