from langchain_core.prompts import PromptTemplate

prompt_example = PromptTemplate(
    input_variables=["question"],
    template="""Responde la siguiente pregunta
    ## Pregunta:
    {question}
    """
    )

