import os
from flask import Flask, request, jsonify, send_file
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route("/")
def index():
    return send_file("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    return jsonify({"response": f"Vastaan testiviestiin: {message}"})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

