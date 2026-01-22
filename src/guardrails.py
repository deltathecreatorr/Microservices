import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

FIREBASE_DB = os.environ.get("FIREBASE_DB")
BASE_URL = f"https://{FIREBASE_DB}-default-rtdb.europe-west1.firebasedatabase.app/"

@app.route('/guardrails/<id>', methods=['PUT'])
def create_guardrail(id):
    """
    Handles the creation of a guardrail
    
    Expects a JSON payload with 'id', a regular expression 'regx', and a substitution string 'sub'.
    Stores the guardrail in the Firebase Realtime Database.
    Returns the created guardrail in a JSON response.
    """
    
    if not FIREBASE_DB:
        return jsonify({"error": "FIREBASE_DB environment variable not set"}), 500

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
    """
    Handles the deletion of a specified guardrail from the Firebase Realtime Database.
    
    Expects the guardrail ID as a parameter in the URL.
    Deletes the guardrail and then returns a success message in a JSON response.
    """
    
    if not FIREBASE_DB:
        return jsonify({"error": "FIREBASE_DB environment variable not set"}), 500

    try:
        firebase_url = f"{BASE_URL}/guardrails/{id}.json"
        response = requests.delete(firebase_url)

        if response.status_code == 200:
            return jsonify({"message": f"Guardrail {id} deleted successfully"}), 200
        else:
            return jsonify({"error": "Failed to delete guardrail", "details": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/guardrails/<id>', methods = ['GET'])
def read_guardrail(id):
    """
    Gets the information about a specified guardrail using the guardrail ID
    
    Expects the guardrail ID as a parameter in the URL.
    Gets the guardrail informations and returns them in a JSON response.
    """

    if not FIREBASE_DB:
        return jsonify({"error": "FIREBASE_DB environment variable not set"}), 500

    try:
        firebase_url = f"{BASE_URL}/guardrails/{id}.json"
        response = requests.get(firebase_url)

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"error": "Failed to read guardrail", "details": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/guardrails', methods=['GET'])
def list_guardrails():
    """
    Gets all information about the guardrails
    
    Returns all the guardrails stored in the Firebase Realtime Database as a JSON response object.
    """
    
    if not FIREBASE_DB:
        return jsonify({"error": "FIREBASE_DB environment variable not set"}), 500

    try:
        firebase_url = f"{BASE_URL}/guardrails.json"
        response = requests.get(firebase_url)

        if response.status_code == 200:
            data = response.json()
            if data is None:
                return jsonify([]), 200
            rails = list(data.keys())
            return jsonify(rails), 200
        else:
            return jsonify({"error": "Failed to list guardrails", "details": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=3001, debug=True)
    