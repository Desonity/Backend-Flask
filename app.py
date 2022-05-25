import json
import uuid
import asyncio
from flask import Flask, render_template, session, request
from static.py.Sign import Sign_Transaction
from decouple import config
import requests

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

@app.route("/", methods=["GET"])
def index():
    return "NEVER GONNA GIVE YOU UP, NEVER GONNA LET YOU DOWN, NEVER GONNA RUN AROUND AND DESERT YOU"


@app.route("/login", methods=["GET", "POST"])
def home():
    appname = request.args.get("appname")
    uuid_token = request.args.get("uuid")
    derive = request.args.get("derive")
    session["uuid"] = uuid_token

    if is_valid_uuid(uuid_token):
        return render_template("home.html", data={"appname": appname, "derive": derive})
    else:
        return render_template("home.html", data={"error": "Invalid Data"})

@app.route("/success", methods=["GET"])
def success():
    session.clear()
    return render_template("success.html")

@app.route("/getKey", methods=["POST"])
def getKey():
    data = request.get_json(force=True)
    if data is None:
        return (400, "")
    uuid_token = data["uuid"]
    if is_valid_uuid(uuid_token):
        if uuid_token in AUTH_DATA:
            data = AUTH_DATA[uuid_token]
            del AUTH_DATA[uuid_token]
            return data
        else:
            return ""


@app.route("/setKey", methods=["GET","POST"])
def setKey():
    # once logged in, you can perform actions on this public key
    data = request.get_json(force=True)
    if data is None:
        return (400, "")
    uuid_token = session["uuid"]
    print(data)
    publicKey = data["publicKey"]
    if "derivedKey" not in data:
        AUTH_DATA[uuid_token] = {"publicKey": publicKey}
        print("pubKey login success")
        return "OK"
    derivedKey = data["derivedKey"]
    derivedSeed = data["derivedSeedHex"]
    accessSignature = data["accessSignature"]
    expirationBlock = data["expirationBlock"]
    payload = {
        "OwnerPublicKeyBase58Check": publicKey,
        "DerivedPublicKeyBase58Check": derivedKey,
        "ExpirationBlock": expirationBlock,
        "AccessSignature": accessSignature,
        "DeleteKey": False,
        "DerivedKeySignature": True,
        "MinFeeRateNanosPerKB": 1700,
        # "TransactionSpendingLimitHex": txnSpendingLimitHex,
    }
    try:
        txnSpendingLimitHex = data["transactionSpendingLimitHex"]
        payload["TransactionSpendingLimitHex"] = txnSpendingLimitHex
    except:
        print("didnot find txn limit")


    res = requests.post(BASE_API + "authorize-derived-key", json=payload)
    if res.status_code == 200:
        txnHex = res.json()["TransactionHex"]
        payload1 = {
            "TransactionHex": txnHex,
            "ExtraData": {"DerivedPublicKey":derivedKey}
        }
        res1 = requests.post(BASE_API + "append-extra-data", json=payload1)
        if res1.status_code == 200:
            txnHexFinal = res1.json()["TransactionHex"]
            signedTxnHex = Sign_Transaction(derivedSeed, txnHexFinal)
            submit = requests.post(BASE_API + "submit-transaction", json={"TransactionHex": signedTxnHex})
            if submit.status_code == 200:
                AUTH_DATA[uuid_token] = {"publicKey": publicKey, "derivedKey": derivedKey, "derivedSeed": derivedSeed}
                print("derive login success")
                return "OK"
            else:
                print("submit error ",submit.json())
                return "ERROR"
        else:
            print("append derived error ",res1.json())
            return "ERROR"
    else:
        print("authorise derived error ",res.json())
        return "ERROR"


# @app.route("/signTxn", methods=["POST"])
# def signTxn():
#     data = request.get_json(force=True)
#     txnHex = data["txnHex"]
#     try:
#         seedHex = data["seedHex"]
#     except Exception as e:
#         return "No Seed Hex found", 400
#     return Sign_Transaction(seedHex, txnHex)

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
