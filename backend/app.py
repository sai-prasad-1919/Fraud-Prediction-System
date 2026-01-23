from flask import Flask, request, jsonify
from flask_cors import CORS
from auth import check_login
from predict import predict_risk

app = Flask(__name__)
CORS(app)

# ---------- LOGIN API ----------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = data.get("username")
    pwd = data.get("password")

    if check_login(user, pwd):
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "fail"})


# ---------- PREDICTION API ----------
@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    tid = data.get("id")

    result = predict_risk(tid)

    return jsonify({"risk": result})


if __name__ == "__main__":
    app.run(debug=True)
