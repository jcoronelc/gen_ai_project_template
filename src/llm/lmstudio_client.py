from dotenv import load_dotenv
from crewai import Crew, LLM, Process
from openai import OpenAI
from google import genai
from google.genai import types
from huggingface_hub import InferenceClient
from langchain_community.chat_models import ChatOllama
from ollama import generate
import lmstudio as lms
import requests
import ollama
import os
import asyncio

load_dotenv()
BASE_URL_LM = os.getenv("BASE_URL_LM")
OPENAI_KEY = os.getenv("OPENAI_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class LMStudioClient:
    def __init__(self, model, provider = "lmstudio", base_url=BASE_URL_LM, api_key=OPENAI_KEY):
        self.provider = provider.lower()
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        self.client = self.init_client()
        
    def init_client(self):        
        if self.provider == "lmstudio":
            return lms.get_default_client()
        
    async def call_instance_1(self, prompt_instance, tokens_number, response_format= None):
        async with lms.AsyncClient() as client:
            model = await client.llm.load_new_instance(
                self.model,
                config={"contextLength": tokens_number, "gpu": {"ratio": 0.5}}
            )
            response = await model.respond(prompt_instance, response_format=response_format)
            # print("Response 1: ",response.parsed)
            await model.unload()
            return response.stats, response.parsed

    async def call_instance_2(self, prompt_instance, tokens_number, response_format= None):
        async with lms.AsyncClient() as client:
            model = await client.llm.load_new_instance(
                self.model,
                config={"contextLength": tokens_number, "gpu": {"ratio": 0.5}}
            )
            response = await model.respond(prompt_instance, response_format=response_format)
            # print("Response 2: ",response.parsed)
            await model.unload()
            return response.stats, response.parsed
    
    async def call_instance_3(self, prompt_instance, tokens_number, response_format= None):
        async with lms.AsyncClient() as client:
            model = await client.llm.load_new_instance(
                self.model,
                config={"contextLength": tokens_number, "gpu": {"ratio": 0.5}}
            )
            response = await model.respond(prompt_instance, response_format=response_format)
            # print("Response 2: ",response.parsed)
            await model.unload()
            return response.stats, response.parsed

    def get_model_info(self, model_id: str):
        url = f"{self.base_url}/models/{model_id}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "response": response.text if 'response' in locals() else None}
    
    def get_llm_crew(self):
        return self.llm_crew
       