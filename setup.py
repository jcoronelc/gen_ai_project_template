

provider="llm-studio"   # "openai", "huggingface"
    
models_embedding = {
    0: "text-embedding-all-minilm-l6-v2-embedding",
    1: "text-embedding-nomic-embed-text-v1.5",
}

models_llm = {
    0: 'qwen3-4b-2507',
    1: 'gpt-oss-20b'
}

model_llm_embeddings = models_embedding[0]
model_llm_responses = models_llm[0]