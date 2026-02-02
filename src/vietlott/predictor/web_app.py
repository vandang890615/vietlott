import os
import json
import numpy as np
import pandas as pd
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from lstm_predictor import LSTMPredictor, get_config

app = Flask(__name__)
CORS(app)

# Cache for models to avoid re-training on every request
models = {}

def get_predictions(product_name):
    config = get_config(product_name)
    if not os.path.exists(f"../../{config.raw_path}"):
        return {"error": f"Data file for {product_name} not found."}
    
    df = pd.read_json(f"../../{config.raw_path}", lines=True)
    df = df.iloc[::-1]
    
    max_num = 55 if "655" in product_name else 45
    predictor = LSTMPredictor(window_size=12, max_num=max_num)
    data = predictor.prepare_data(df)
    
    X, y = predictor.create_sequences(data)
    predictor.build_model(input_shape=(X.shape[1], X.shape[2]), output_dim=y.shape[1])
    # For a simple demo, we just train a few epochs or use a pre-trained if we had one
    # To keep web response fast, let's use 20 epochs
    predictor.train(X, y, epochs=20)
    
    last_draws = data[-predictor.window_size:]
    tickets = []
    for i in range(5):
        noise_scale = 0.05 * i
        noise = np.random.normal(0, noise_scale, last_draws.shape)
        ticket = predictor.predict_next(last_draws + noise)
        tickets.append(ticket)
    
    return {"product": product_name, "tickets": tickets}

@app.route('/api/predict/<product>')
def predict(product):
    res = get_predictions(product)
    return jsonify(res)

@app.route('/')
def index():
    return """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vietlott AI Predictor</title>
    <style>
        body { font-family: sans-serif; text-align: center; background-color: #f4f4f9; padding: 20px; }
        .container { max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1 { color: #d32f2f; }
        .btn { padding: 10px 20px; font-size: 16px; cursor: pointer; background: #d32f2f; color: white; border: none; border-radius: 5px; margin: 10px; }
        .btn:disabled { background: #ccc; }
        .ticket { margin: 10px 0; padding: 10px; border-bottom: 1px solid #eee; font-size: 18px; font-weight: bold; }
        .ball { display: inline-block; width: 35px; height: 35px; line-height: 35px; border-radius: 50%; background: #ffc107; margin: 5px; color: #333; box-shadow: 1px 1px 3px rgba(0,0,0,0.2); }
        #loading { display: none; font-style: italic; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Vietlott AI (LSTM)</h1>
        <p>Chọn loại xổ số để xem dự đoán từ AI</p>
        <button class="btn" onclick="fetchPredict('power645')">Dự đoán Power 6/45</button>
        <button class="btn" onclick="fetchPredict('power655')">Dự đoán Power 6/55</button>
        
        <div id="loading">AI đang suy nghĩ (Training model)... Vui lòng đợi trong giây lát...</div>
        <div id="results"></div>
    </div>

    <script>
        async function fetchPredict(product) {
            const btn = event.target;
            const loading = document.getElementById('loading');
            const results = document.getElementById('results');
            
            loading.style.display = 'block';
            results.innerHTML = '';
            document.querySelectorAll('.btn').forEach(b => b.disabled = true);
            
            try {
                const response = await fetch(`/api/predict/${product}`);
                const data = await response.json();
                
                if (data.error) {
                    results.innerHTML = `<p style="color:red">${data.error}</p>`;
                } else {
                    let html = `<h3>Gợi ý cho ${product.toUpperCase()}</h3>`;
                    data.tickets.forEach((t, i) => {
                        html += `<div class="ticket">Vé ${i+1}: `;
                        t.forEach(n => {
                            html += `<span class="ball">${n.toString().padStart(2, '0')}</span>`;
                        });
                        html += `</div>`;
                    });
                    results.innerHTML = html;
                }
            } catch (e) {
                results.innerHTML = '<p style="color:red">Lỗi kết nối máy chủ.</p>';
            } finally {
                loading.style.display = 'none';
                document.querySelectorAll('.btn').forEach(b => b.disabled = false);
            }
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    # Make sure we are in the correct directory to find data
    app.run(host='0.0.0.0', port=5000)
