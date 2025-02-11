from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig
from scipy.special import softmax
import numpy as np

app = Flask(__name__)
CORS(app) 

tokenizer = AutoTokenizer.from_pretrained("C:\Users\Jai\Desktop\MP\code\Backend\Trained model")
config = AutoConfig.from_pretrained("C:\Users\Jai\Desktop\MP\code\Backend\Trained model")
model = AutoModelForSequenceClassification.from_pretrained("C:\Users\Jai\Desktop\MP\code\Backend\Trained model")

def preprocess(text):
    new_text = []
    for t in text.split(" "):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)

@app.route('/analyze_sentiment', methods=['POST'])
def analyze_sentiment():
    data = request.get_json()
    if 'text' not in data:
        return jsonify({'error': 'Text parameter not found'}), 400
    text = data['text']
    text = preprocess(text)
    encoded_input = tokenizer(text, return_tensors='pt')
    output = model(**encoded_input)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)
    ranking = np.argsort(scores)[::-1]
    results = []
    for i in range(scores.shape[0]):
        label = config.id2label[ranking[i]]
        score = np.round(float(scores[ranking[i]]), 4)
        results.append({'label': label, 'score': score})
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
