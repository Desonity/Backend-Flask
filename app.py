import json
import uuid
import asyncio
from flask import Flask, render_template, session, request
from static.py.Sign import Sign_Transaction
from decouple import config

BASE_API = "https://diamondapp.com/api/v0/"

app = Flask(__name__)
# feel free to change secret key but keep it private
# This is used to store data in flask session locally in the browser
# idk how safe this is tho
app.secret_key = config("FLASK_SECRET_KEY")
app.debug = True

AUTH_DATA = dict({})


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


@app.route("/login/<uuid_token>", methods=["GET", "POST"])
def home(uuid_token):
    requester_name = request.args.get("appname")
    try:
        logged_in_key = session["LoggedInUser"]
    except Exception:
        logged_in_key = None

    if logged_in_key:
        if is_valid_uuid(uuid_token):
            AUTH_DATA[uuid_token] = logged_in_key
            del session["LoggedInUser"]
            return render_template("home.html", data={"loggedInKey": logged_in_key, "requester": requester_name})
        else:
            return render_template("home.html", data={"error": "Invalid UUID"})
    else:
        return render_template("home.html", data={"requester": requester_name})


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("LoggedInUser", None)
    return "OK"


@app.route("/getKey", methods=["POST"])
def getKey():
    data = request.get_json(force=True)
    uuid_token = data["uuid"]
    if is_valid_uuid(uuid_token):
        if uuid_token in AUTH_DATA:
            pkey = AUTH_DATA[uuid_token]
            del AUTH_DATA[uuid_token]
            return pkey
        else:
            return ""


@app.route("/setKey", methods=["POST"])
def setKey():
    # once logged in, you can perform actions on this public key
    data = request.get_json(force=True)
    session["LoggedInUser"] = data["PublicKey"]
    return "OK"


@app.route("/signTxn", methods=["POST"])
def signTxn():
    data = request.get_json(force=True)
    txnHex = data["txnHex"]
    try:
        seedHex = data["seedHex"]
    except Exception as e:
        return "No Seed Hex found", 400
    return Sign_Transaction(seedHex, txnHex)

    # @app.route("/create-txn", methods=["POST"])
    # def create_txn():
    #     payload = request.get_json(force=True)
    #     endpoint = BASE_API + payload["Endpoint"]
    #     data = payload["Data"]
    #     res = requests.post(endpoint, json=data)
    #     if res.status_code == 200:
    #         return res.json()["TransactionHex"]
    #     else:
    #         print(res.status_code, res.text)
    #         return None

    # @app.route("/submit-txn", methods=["POST"])
    # def submit():
    #     payload = request.get_json(force=True)
    #     endpoint = BASE_API + "submit-transaction"
    #     data = {
    #         "TransactionHex": payload["TransactionHex"]
    #     }
    #     res = requests.post(endpoint, json=data)
    #     if res.status_code == 200:
    #         return res.json()["TxnHashHex"]
    #     else:
    #         print(res.status_code, res.text)
    #         return None
