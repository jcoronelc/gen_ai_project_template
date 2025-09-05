

provider="llm-studio"   # "openai", "huggingface"
    
models_embedding = {
    0: "text-embedding-all-minilm-l6-v2-embedding",
    1: "text-embedding-nomic-embed-text-v1.5",
    2: "text-embedding-qwen3-embedding-0.6b",
    3: 'text-embedding-qwen3-embedding-8b'
}

models_llm = {
    0: "meta-llama-3-8b-instruct-bpe-fix",
    1: "deepseek-r1-distill-llama-8b",
    2: "mistral-nemo-instruct-2407",
    3: 'gemma-3-4b-it',
    4: 'utplllama',
    5: 'llama-3.2-3b-instruct', 
    6: 'mistralfinetuning',
    7: 'qwen3-4b-2507',
    8: 'gpt-oss-20b'
}

model_llm_embeddings = models_embedding[2]
model_llm_responses = models_llm[8]