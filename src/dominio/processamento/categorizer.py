import re

import joblib
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

le = joblib.load("/home/lev0x/scratches/categorizer/label_encoder.joblib")


def normalize_value(text):
    return re.sub(r"R\$ ?[\d\.,]+|[\d\.,]+", "<VALOR>", text)


def load_model_and_tokenizer(
    model_path="/home/lev0x/scratches/categorizer/results/checkpoint-550",
):
    tokenizer = AutoTokenizer.from_pretrained("neuralmind/bert-base-portuguese-cased")

    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    model.eval()

    return model, tokenizer


def predict_category(message: str, model, tokenizer):
    message = normalize_value(message)

    inputs = tokenizer(message, return_tensors="pt", truncation=True, padding=True, max_length=64)

    with torch.no_grad():
        outputs = model(**inputs)
        predicted = torch.argmax(outputs.logits, dim=1).item()

    return le.inverse_transform([predicted])[0]
