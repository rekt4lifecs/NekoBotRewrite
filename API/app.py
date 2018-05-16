from flask import Flask, request, jsonify
import pymysql, redis
import config

app = Flask(__name__)

def getuser(user:int):
    connection = pymysql.connect(host="localhost", user="root", password=config.dbpass,
                                 db="nekobot")
    db = connection.cursor()
    if not db.execute(f"SELECT 1 FROM economy WHERE userid = {user}"):
        return False
    else:
        return True

def getbal(user:int):
    connection = pymysql.connect(host="localhost", user="root", password=config.dbpass,
                                 db="nekobot")
    db = connection.cursor()
    if db.execute(f"SELECT balance FROM economy WHERE userid = {user}"):
        balance = int(db.fetchone()[0])
    else:
        balance = 0
    return balance

def getlvl(user:int):
    r = redis.StrictRedis(host="localhost", port=6379, db=0)
    lvl = r.get(f"{user}-lvl")
    if not lvl:
        lvl = 0
    else:
        lvl = int(lvl)
    return lvl

@app.route('/', methods=["GET"])
def main():
    user = request.args.get("user")
    if user is None:
        return jsonify({"message": "No user ID provided."}), 400
    try:
        user = int(user)
    except:
        return jsonify({"message": "Invalid User ID"}), 400
    if not isinstance(user, int):
        return jsonify({"message": "Invalid User ID"}), 400
    if not getuser(user):
        return jsonify({"message": "Invalid User ID"}), 400
    return jsonify({
        "balance": getbal(user),
        "level": getlvl(user)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9081)