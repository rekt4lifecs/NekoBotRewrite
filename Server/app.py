from flask import Flask, request
from colorthief import ColorThief
from io import BytesIO
import redis
import requests
import base64

app = Flask(__name__)
db = redis.Redis()
default_color = 0xDEADBF

@app.route("/")
def index():
    return "OK"

@app.route("/dominant")
def dominant():
    url = request.args.get("url")
    if url is None:
        return "No url arg", 400
    try:
        data = BytesIO(requests.get(url).content)
    except:
        return str(default_color)
    r, g, b = ColorThief(data).get_color()
    color = int(format(r << 16 | g << 8 | b, "06" + "x"), 16)
    db.set("color:{}".format(base64.b64encode(url.encode("utf8")).decode("utf8")), color, ex=604800)
    return str(color)

if __name__ == "__main__":
    app.run("localhost", 8096, True)
