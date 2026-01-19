import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

FIREBASE_DB = os.environ.get("FIREBASE_DB")
BASE_URL = f"https://{FIREBASE_DB}-default-rtdb.europe-west1.firebasedatabase.app"

@app.route('/guardrails/<id>', methods=['PUT'])
def create_guardrail(id):
    if not FIREBASE_DB:
        return jsonify({"error": "FIREBASE_DB environment variable is not set"}), 500
    
    try:
        data = request.get_json()

        required = {"id", "regx", "sub"}
        if not data or not required.issubset(data.keys()):
            return jsonify({"error": f"Missing required fields: {required}"}), 400
        
        data["id"] = id 

        firebase_url = f"{BASE_URL}/guardrails/{id}.json"
        response = requests.put(firebase_url, json=data)

        if response.status_code in [200, 201]:
            return jsonify(response.json()), 200
        else:
            return jsonify({"error": "Failed to create guardrail", "details": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/guardrails/<id>', methods=['DELETE'])
def delete_guardrail(id):
    pass

@app.route('/guardrails/<id>', methods = ['GET'])
def read_guardrail(id):
    pass

@app.route('/guardrails', methods=['GET'])
def list_guardrails():
    pass