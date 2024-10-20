from flask import Flask, jsonify
from src import api

app = Flask(__name__)
api.init_app(app)


@app.route("/")
def root():
    return jsonify(message="Hello World")


@app.route("/hello/<name>")
def say_hello(name: str):
    return jsonify(message=f"Hello {name}")


if __name__ == "__main__":
    app.run(debug=True)
