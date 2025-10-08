# 🧠 GenAI Project Template

Plantilla base para proyectos de **Inteligencia Artificial Generativa (GenAI)**.  
Esta estructura está diseñada para acelerar el desarrollo de aplicaciones que integran modelos de lenguaje, flujos de agentes, procesamiento de datos y almacenamiento vectorial.  

Permite mantener un entorno **modular, escalable y reproducible**, ideal para proyectos basados en **OpenAI, Anthropic, HuggingFace, LangChain, LlamaIndex, o modelos locales (LM Studio, Ollama, vLLM, etc.)**.

---

## 📁 Estructura Completa del Proyecto

```
gen_ai_project_template/
│
├── config/                          # Configuración general
│   ├── settings.yaml                # Configuración principal en YAML
│   ├── model_configs.json           # Configuraciones específicas de modelos
│  
├── data/                            # Almacenamiento de datos
│   ├── raw/                         # Datos crudos sin procesar
│   │   ├── documents/               # Documentos PDF, TXT, DOCX
│   │   ├── datasets/                # Conjuntos de datos estructurados
│   │   └── images/                  # Imágenes para procesamiento multimodal
│   ├── processed/                   # Datos limpios/listos para embeddings
│   │   ├── chunked_text/            # Texto dividido en chunks
│   │   └── normalized_data/         # Datos normalizados
│   ├── embeddings/                  # Vectores generados
│   │   ├── faiss_index/             # Índices FAISS
│   │   ├── chroma_db/               # Base de datos Chroma
│   │   └── embeddings_cache/        # Caché de embeddings
│   ├── cache/                       # Archivos temporales
│   │   ├── llm_cache/               # Caché de respuestas de LLM
│   │   └── query_cache/             # Caché de consultas
│   └── output/                      # Resultados de inferencia
│       ├── generated_content/       # Contenido generado
│       ├── reports/                 # Reportes y análisis
│       └── exports/                 # Datos exportados
│
├── logs/                            # Archivos de log
│   ├── app.log                      # Log principal de la aplicación
│   ├── error.log                    # Log de errores
│   └── performance.log              # Log de rendimiento
│
├── src/                             # Código fuente principal
│   ├── llm/                         # Wrappers e interfaces con LLMs
│   │   ├── __init__.py
│   │   ├── base_llm.py              # Clase base abstracta para LLMs
│   │   ├── openai_client.py         # Cliente para OpenAI
│   │   ├── anthropic_client.py      # Cliente para Anthropic Claude
│   │   ├── huggingface_client.py    # Cliente para HuggingFace
│   │   ├── local_models.py          # Modelos locales (Ollama, vLLM)
│   │   └── model_registry.py        # Registro y gestión de modelos
│   │
│   ├── chain/                       # Cadenas y flujos de razonamiento
│   │   ├── __init__.py
│   │   ├── base_chain.py            # Clase base para cadenas
│   │   ├── sequential_chain.py      # Cadenas secuenciales
│   │   ├── router_chain.py          # Enrutamiento de cadenas
│   │   ├── tools/                   # Herramientas auxiliares
│   │   │   ├── __init__.py
│   │   │   ├── web_search.py        # Búsqueda web
│   │   │   ├── calculator.py        # Calculadora
│   │   │   ├── code_executor.py     # Ejecutor de código
│   │   │   └── file_processor.py    # Procesador de archivos
│   │   └── agents/                  # Definición de agentes
│   │       ├── __init__.py
│   │       ├── base_agent.py        # Agente base
│   │       ├── react_agent.py       # Agente ReAct
│   │       ├── conversational_agent.py
│   │       └── specialized_agents/  # Agentes especializados
│   │           ├── data_analyst.py
│   │           ├── code_assistant.py
│   │           └── research_assistant.py
│   │
│   ├── prompt/                      # Gestión avanzada de prompts
│   │   ├── __init__.py
│   │   ├── prompt_manager.py        # Gestor principal de prompts
│   │   ├── template_engine.py       # Motor de plantillas
│   │   ├── templates/               # Plantillas de prompts
│   │   │   ├── system_prompts.py    # Prompts del sistema
│   │   │   ├── task_prompts.py      # Prompts de tareas
│   │   │   └── few_shot_examples.py # Ejemplos few-shot
│   │   └── prompt_optimizer.py      # Optimizador de prompts
│   │
│   ├── db/                          # Conectores de bases de datos
│   │   ├── __init__.py
│   │   ├── base_database.py         # Clase base para DB
│   │   ├── vector_db/               # Vector stores
│   │   │   ├── __init__.py
│   │   │   ├── base_vector_db.py    # Clase base vector DB
│   │   │   ├── faiss_client.py      # Cliente FAISS
│   │   │   ├── chroma_client.py     # Cliente Chroma
│   │   │   ├── pinecone_client.py   # Cliente Pinecone
│   │   │   └── weaviate_client.py   # Cliente Weaviate
│   │   └── postgres_db/             # Integración con PostgreSQL
│   │       ├── __init__.py
│   │       ├── postgres_client.py   # Cliente PostgreSQL
│   │       └── models.py            # Modelos de datos SQL
│   │
│   ├── utils/                       # Utilidades genéricas
│   │   ├── __init__.py
│   │   ├── logger.py                # Sistema de logging
│   │   ├── file_utils.py            # Utilidades de archivos
│   │   ├── validation.py            # Validación de datos
│   │   └── decorators.py            # Decoradores útiles
│   │
│   └── func/                        # Funciones específicas del dominio
│       ├── __init__.py
│       ├── data_processing.py       # Procesamiento de datos
│       ├── content_generation.py    # Generación de contenido
│       ├── analysis_functions.py    # Funciones de análisis
│       └── domain_specific.py       # Funciones específicas del negocio
│
├── testing/                         # Pruebas unitarias y de integración
│   ├── __init__.py
│   ├── unit/                        # Tests unitarios
│   │   ├── test_llm.py
│   │   ├── test_chains.py
│   │   ├── test_prompts.py
│   ├── integration/                 # Tests de integración
│   │   ├── test_agents.py
│   │   ├── test_vector_db.py
│   │   └── test_end_to_end.py
│   └── notebooks/                    # Datos de prueba
│      
│
├── docs/                            # Documentación
│   ├── api/                         # Documentación de API
│   ├── guides/                      # Guías de uso
│   └── examples/                    # Ejemplos de código
│
|
├── scripts/                         # Scripts auxiliares
│   ├── setup_environment.sh         # Configuración del entorno
│   ├── data_processing.py           # Procesamiento de datos
│   ├── model_training.py            # Entrenamiento de modelos
│   └── deployment.py                # Scripts de despliegue
│
├── main.py                          # Punto de entrada principal
├── requirements.txt                 # Dependencias de Python
├── setup.py                         # Instalación como paquete
├── .env                             # Variables de entorno ejemplo
├── .gitignore                       # Archivos ignorados por Git
└── README.md                        # Este archivo
```

---

## 🚀 Instalación y Uso Rápido

### 1. Clonar el repositorio
```bash
git clone https://github.com/jcoronelc/gen_ai_project_template.git
cd gen_ai_project_template
```

### 2. Configurar entorno virtual
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate     # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Para desarrollo
```

### 4. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus claves API y configuraciones
```

### 5. Ejecutar aplicación principal
```bash
python main.py
```
---

## 🔧 Módulos Principales

| Módulo | Descripción |
|--------|-------------|
| **`src/llm/`** | Integración con modelos de lenguaje (OpenAI, Claude, HuggingFace, Locales (LM Studio,  Ollama) etc.) |
| **`src/chain/`** | Cadenas de razonamiento, agentes y flujos de conversación |
| **`src/prompt/`** | Gestión de prompts dinámicos y plantillas personalizadas |
| **`src/db/`** | Conexiones a bases de datos tradicionales y vectoriales |
| **`src/utils/`** | Utilidades: logging, validaciones, parsers, etc. |
| **`src/func/`** | Funciones específicas del dominio o negocio |
| **`testing/`** | Tests unitarios y de integración automatizados |
| **`scripts/`** | Scripts para setup, procesamiento y deployment |


## 📚 Ejemplos de Uso

### Uso Básico con OpenAI
```python
from src.llm.openai_client import OpenAIClient
from src.prompt.prompt_manager import PromptManager

# Inicializar cliente
llm = OpenAIClient()

# Gestión de prompts
prompt_manager = PromptManager()
system_prompt = prompt_manager.get_system_prompt("assistant")
user_prompt = prompt_manager.render_template("analysis", data=my_data)

# Ejecutar consulta
response = llm.generate(system_prompt, user_prompt)
```

### Pipeline RAG Completo
```python
from src.chain.agents.research_assistant import ResearchAssistant
from src.db.vector_db.faiss_client import FaissClient

# Inicializar componentes
vector_db = FaissClient()
agent = ResearchAssistant(vector_db=vector_db)

# Ejecutar investigación
result = agent.research(
    query="Tendencias actuales en machine learning",
    sources=["arxiv", "web"]
)
```

### Agente Conversacional con Herramientas
```python
from src.chain.agents.conversational_agent import ConversationalAgent
from src.chain.tools.web_search import WebSearchTool
from src.chain.tools.calculator import CalculatorTool

# Configurar agente con herramientas
tools = [WebSearchTool(), CalculatorTool()]
agent = ConversationalAgent(tools=tools)

# Interactuar con el agente
response = agent.chat("¿Cuál es el PIB de España y calcula el 15%?")
```

---

## 🛠️ Desarrollo

### Agregar Nuevo Modelo LLM
1. Crear clase en `src/llm/`
2. Heredar de `BaseLLM`
3. Implementar métodos `generate()` y `stream()`
4. Registrar en `model_registry.py`

### Crear Nueva Cadena
1. Definir en `src/chain/`
2. Heredar de `BaseChain`
3. Implementar lógica de ejecución
4. Agregar tests en `testing/unit/test_chains.py`

### Agregar Nueva Herramienta
1. Crear en `src/chain/tools/`
2. Implementar interfaz de herramienta
3. Documentar parámetros y retorno
4. Agregar a registro de herramientas

---

## 📦 Despliegue

### Instalación como Paquete
```bash
pip install -e .
```
---

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

---

## 📄 Licencia

Distribuido bajo la Licencia MIT. Ver `LICENSE` para más información.

---

