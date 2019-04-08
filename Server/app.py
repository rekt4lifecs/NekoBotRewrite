from flask import Flask, request, jsonify
from colorthief import ColorThief

app = Flask(__name__)

@app.route("/")
def index():
    return "OK"

if __name__ == "__main__":
    app.run("localhost", 8096, True)
