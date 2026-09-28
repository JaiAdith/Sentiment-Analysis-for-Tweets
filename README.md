# Sentiment Analysis for Tweets

A full-stack web app that classifies the sentiment of tweets as **positive**, **neutral**, or **negative**. Users can analyze a single tweet they type in, or fetch the 10 most recent tweets from any X (Twitter) account and see per-tweet sentiment plus an overall summary.

## How It Works

```
Browser (AngularJS)
   │  1. username
   ▼
Node.js / Express proxy  ──►  RapidAPI (twitter154)  ──►  latest tweets
   │  2. tweets
   ▼
Flask inference API  ──►  Twitter-RoBERTa model  ──►  label + confidence per tweet
```

1. The frontend sends the username to the **Express proxy**, which fetches recent tweets from RapidAPI. The proxy keeps the API key on the server instead of exposing it in the browser.
2. The tweets are sent in one batch to the **Flask API**.
3. Flask normalizes mentions (`@name` → `@user`) and links (`https://...` → `http`), matching how the model's training data was prepared.
4. The tokenizer converts text to token IDs, the model outputs one raw score (logit) per class, and **softmax** turns those into probabilities.
5. The frontend shows each tweet's predicted label and confidence, and the overall sentiment is the most frequent label.

## Model

[`cardiffnlp/twitter-roberta-base-sentiment-latest`](https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest), a RoBERTa-base model that Cardiff NLP further pretrained on a large corpus of tweets and fine-tuned for 3-class sentiment on the TweetEval benchmark. This project uses the model as-is for inference; it does not perform additional fine-tuning.

**Why a Twitter-specific model:** tweets are short and full of slang, emojis, hashtags, and misspellings. A model pretrained on real tweets handles that language far better than one trained on books and Wikipedia.

## Project Structure

```
├── Backend/
│   ├── server.py          # Flask inference API (model loading, preprocessing, prediction)
│   ├── requirements.txt   # Python dependencies
│   ├── backend.js         # Express proxy for fetching tweets
│   ├── package.json       # Node dependencies
│   └── .env.example       # Template for the RapidAPI key
└── Frontend/
    ├── 11.html            # Landing page
    ├── 22.html            # Mode selection
    ├── 44.html            # Analyze a custom tweet
    ├── user_analysis.html # Analyze an X user's recent tweets
    └── 77.css
```

## Setup

### 1. Flask inference API

```bash
cd Backend
pip install -r requirements.txt
python server.py
```

Runs on `http://127.0.0.1:5000`. The model downloads from HuggingFace on first run (~500 MB).

### 2. Express tweet proxy

```bash
cd Backend
npm install
cp .env.example .env      # Windows: copy .env.example .env
# Add your RapidAPI key to .env
npm start
```

Runs on `http://localhost:3000`. Get a key by subscribing to the `twitter154` API on [RapidAPI](https://rapidapi.com).

### 3. Frontend

Open `Frontend/11.html` in a browser (or serve the folder with `python -m http.server`).

## API

| Method | Endpoint | Body | Returns |
|---|---|---|---|
| GET | `/health` | – | Service status |
| POST | `/analyze_sentiment` | `{"text": "..."}` | Labels ranked by probability |
| POST | `/analyze_batch` | `{"texts": ["...", "..."]}` | Ranked labels for each text |

Example:

```bash
curl -X POST http://127.0.0.1:5000/analyze_sentiment \
  -H "Content-Type: application/json" \
  -d '{"text": "Loving the new update @dev https://t.co/abc"}'
```

```json
[
  {"label": "positive", "score": 0.9812},
  {"label": "neutral", "score": 0.0151},
  {"label": "negative", "score": 0.0037}
]
```

## Limitations and Future Work

- **No accuracy evaluation yet.** Scores shown are the model's confidence (softmax probability), not measured accuracy. Next step: evaluate on the labeled TweetEval test set and report accuracy, macro F1, and a confusion matrix.
- **No domain fine-tuning.** The pretrained model could be fine-tuned on tweets from a specific domain (e.g. product feedback) for better results there.
- **Two separate backends.** The proxy and inference API could be merged into a single Python service.
- **Sarcasm and mixed sentiment** remain difficult for the model.

## Tech Stack

Python, Flask, HuggingFace Transformers, PyTorch, Node.js, Express, AngularJS, Materialize CSS
