import os
from flask import Flask, request, jsonify, send_file, session
from dotenv import load_dotenv

from chat_core import chat, new_conversation

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")


def _get_history():
    return session.get("history", new_conversation())


def _set_history(history):
    session["history"] = history


@app.route("/")
def index():
    return send_file("index.html")


@app.route("/api/chat", methods=["POST"])
def chat_endpoint():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")

    history = _get_history()
    response = chat(history, message)
    _set_history(history)

    return jsonify({"response": response})


@app.route("/api/reset", methods=["POST"])
def reset_endpoint():
    session.pop("history", None)
    return jsonify({"status": "reset"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
