
from src.prompt.templates import prompt_example

def get_prompt_template(prompt_id: str, doc: dict):

    if prompt_id == "prompt_example":
        prompt = prompt_example.format(question = doc["question"])
        return prompt
    else:
        raise ValueError(f"Prompt no registrado: {prompt_id}")
    