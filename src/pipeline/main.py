
from setup import model_llm_responses, provider
from llm import LLMClient
from prompt import prompt_competencies
from dotenv import load_dotenv

import os

load_dotenv()

BASE_URL_LM = os.getenv("BASE_URL_LM")
OPENAI_KEY = os.getenv("OPENAI_KEY")

def main():

    llm_client = LLMClient(
        provider=provider,   # o "openai", "huggingface"
        model=model_llm_responses,
        base_url=BASE_URL_LM,  
        api_key=OPENAI_KEY       
    )

    text = "cual es el pais mas grande del mundo"
    prompt_completed = prompt_competencies(text)
    response = llm_client.call(prompt_completed)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('... Proceso finalizado ...')