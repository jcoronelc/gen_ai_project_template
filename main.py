
from gen_ai_project_template.src.utils.logger import setup_print_logger
from gen_ai_project_template.src.llm.local_models import LLMClient
from gen_ai_project_template.src.prompt.templates.system_prompts import prompt_one
from gen_ai_project_template.src.utils.decorators import load_config 
from gen_ai_project_template.src.db.db_utils import get_engine, fun_connection_params
from dotenv import load_dotenv

import os
import sys

load_dotenv()

path_config = "config/config.yaml"
path_model = "config/model_config.yaml"
BASE_URL_LM = os.getenv("BASE_URL_LM")
OPENAI_KEY = os.getenv("OPENAI_KEY")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def set_enviroment():
    config = load_config(path_config)
    catalog_conn = fun_connection_params(**config['catalog_db'])
    engine = get_engine(catalog_conn)
    return engine

def set_client_llm():
    # Cliente LLM
    config = load_config(path_model)
    catalog_model = config['catalog_model']
    provider = catalog_model['provider']
    llm_name = catalog_model['llm_name']

    model_id = config[provider]['models'][llm_name]['id']

    llm_client = LLMClient(
        provider=provider,
        model_name=model_id,
        base_url=BASE_URL_LM,
        api_key=OPENAI_KEY
    )
    return llm_client

def main():

    # log
    setup_print_logger(f"", log_name="log")
    # engine = set_enviroment()  #setting database enviroment
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