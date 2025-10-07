
from setup import model_llm_responses, provider
from gen_ai_project_template.src.utils.logging_utils import setup_print_logger
from src.llm.llm_client import LLMClient
from gen_ai_project_template.src.prompt.templates import prompt_one
from dotenv import load_dotenv

import os

load_dotenv()

BASE_URL_LM = os.getenv("BASE_URL_LM")
OPENAI_KEY = os.getenv("OPENAI_KEY")


def set_client_llm():
    # LLM client
    llm_client = LLMClient(
        provider=provider,
        model=model_llm_responses,
        base_url=BASE_URL_LM,
        api_key=OPENAI_KEY
    )
    return llm_client

def main():

    # log
    setup_print_logger(f"", log_name="log")
    llm_client = set_client_llm() #setting llm models

    text = "cual es el pais mas grande del mundo"
    prompt_completed = prompt_one(text)
    response = llm_client.call(prompt_completed)
    print("####### RESPUESTA ######")
    print(response)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('... Proceso finalizado ...')