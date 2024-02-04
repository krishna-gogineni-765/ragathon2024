from transformers import AutoModel, AutoTokenizer

model_name = "google/siglip-base-patch16-256-multilingual"

# Pre-download model and tokenizer
model = AutoModel.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

print(f"Downloaded {model_name} successfully.")