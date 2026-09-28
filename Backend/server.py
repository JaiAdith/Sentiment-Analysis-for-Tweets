"""
Flask inference API for tweet sentiment analysis.

Model: cardiffnlp/twitter-roberta-base-sentiment-latest
  - RoBERTa-base further pretrained on tweets and fine-tuned for
    3-class sentiment (negative / neutral / positive) by Cardiff NLP.
  - Used as-is (no additional fine-tuning in this project).

Endpoints:
  GET  /health                 -> service status
  POST /analyze_sentiment      -> {"text": "..."}          -> ranked labels for one tweet
  POST /analyze_batch          -> {"texts": ["...", ...]}  -> ranked labels for many tweets

Run:
  pip install -r requirements.txt
  python server.py
"""

import os

import numpy as np
import torch
from flask import Flask, jsonify, request
from flask_cors import CORS
from scipy.special import softmax
from transformers import AutoConfig, AutoModelForSequenceClassification, AutoTokenizer

# Load from HuggingFace by default; override with a local folder via MODEL_PATH
MODEL_PATH = os.environ.get("MODEL_PATH", "cardiffnlp/twitter-roberta-base-sentiment-latest")
MAX_BATCH_SIZE = 50
MAX_TEXT_LENGTH = 1000  # characters

app = Flask(__name__)
CORS(app)

print(f"Loading model: {MODEL_PATH}")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
config = AutoConfig.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()  # inference mode: disables dropout
print("Model loaded.")


def preprocess(text: str) -> str:
    """
    Normalize user mentions and links the same way the model's training data was
    normalized, so inputs match the distribution the model learned from.
    """
    tokens = []
    for t in text.split(" "):
        if t.startswith("@") and len(t) > 1:
            t = "@user"
        elif t.startswith("http"):
            t = "http"
        tokens.append(t)
    return " ".join(tokens)


def predict(texts: list[str]) -> list[list[dict]]:
    """
    Run the model on a batch of texts in a single forward pass.
    Returns, for each text, all labels sorted from most to least likely.
    """
    cleaned = [preprocess(t) for t in texts]
    encoded = tokenizer(
        cleaned,
        return_tensors="pt",
        padding=True,      # pad shorter texts so the batch is a single tensor
        truncation=True,   # cut texts longer than the model's max length
        max_length=512,
    )

    with torch.no_grad():  # no gradients needed for inference
        logits = model(**encoded).logits.numpy()

    results = []
    for row in logits:
        probs = softmax(row)                 # raw logits -> probabilities summing to 1
        ranking = np.argsort(probs)[::-1]    # indices from highest to lowest probability
        results.append([
            {"label": config.id2label[int(i)], "score": round(float(probs[i]), 4)}
            for i in ranking
        ])
    return results


def validate_text(value):
    if not isinstance(value, str) or not value.strip():
        return "Text must be a non-empty string"
    if len(value) > MAX_TEXT_LENGTH:
        return f"Text exceeds {MAX_TEXT_LENGTH} characters"
    return None


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": MODEL_PATH})


@app.route("/analyze_sentiment", methods=["POST"])
def analyze_sentiment():
    data = request.get_json(silent=True) or {}
    text = data.get("text")
    error = validate_text(text)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(predict([text])[0])


@app.route("/analyze_batch", methods=["POST"])
def analyze_batch():
    data = request.get_json(silent=True) or {}
    texts = data.get("texts")
    if not isinstance(texts, list) or not texts:
        return jsonify({"error": "texts must be a non-empty list"}), 400
    if len(texts) > MAX_BATCH_SIZE:
        return jsonify({"error": f"Maximum {MAX_BATCH_SIZE} texts per request"}), 400
    for t in texts:
        error = validate_text(t)
        if error:
            return jsonify({"error": error}), 400
    return jsonify(predict(texts))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=False)
