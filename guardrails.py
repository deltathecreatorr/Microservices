
import database
import re
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/guardrails/<id>', methods=['PUT'])
def create_guardrail(id):
    """
    Handles the creation of a guardrail
    
    Expects a JSON payload with 'id', a regular expression 'regx', and a substitution string 'sub'.
    Stores the guardrail in the Firebase Realtime Database.
    Returns the created guardrail in a JSON response.
    """
    
    data = request.get_json()

    required = {"id", "regx", "sub"}
    if not data or not required.issubset(data.keys()):
        return jsonify({"error": f"Missing required fields: {required}"}), 400
    
    if str(data["id"]) != str(id):
        return jsonify({"error": "ID in URL does not match ID in request body"}), 400

    if database.db.get(id)[0] == 200:
        return jsonify({"error": f"Guardrail with ID {id} already exists"}), 400
    
    try:
        re.compile(data["regx"])
    except re.error as re_err:
        return jsonify({"error": f"Invalid regular expression: {re_err}"}), 400
    
    status_code, response_data = database.db.put(id, data)
    if status_code == 200:
        return jsonify(response_data), 201
    else:
        return jsonify({"error": "Failed to create guardrail", "details": response_data}), status_code

@app.route('/guardrails/<id>', methods=['DELETE'])
def delete_guardrail(id):
    """
    Handles the deletion of a specified guardrail from the Firebase Realtime Database.
    
    Expects the guardrail ID as a parameter in the URL.
    Deletes the guardrail and then returns a success message in a JSON response.
    """
   
    status_code, response_data = database.db.delete(id)
    if status_code == 200:
        return jsonify({"message": f"Guardrail with ID {id} deleted successfully"}), 200
    else:
        return jsonify({"error": "Failed to delete guardrail", "details": response_data}), status_code
    
    
@app.route('/guardrails/<id>', methods = ['GET'])
def read_guardrail(id):
    """
    Gets the information about a specified guardrail using the guardrail ID
    
    Expects the guardrail ID as a parameter in the URL.
    Gets the guardrail informations and returns them in a JSON response.
    """

    status_code, response_data = database.db.get(id)
    if status_code == 200:
        if response_data is None:
            return jsonify({"error": f"Guardrail with ID {id} not found"}), 404
        return jsonify(response_data), 200
    else:
        return jsonify({"error": "Failed to retrieve guardrail", "details": response_data}), status_code


@app.route('/guardrails', methods=['GET'])
def list_guardrails():
    """
    Gets all information about the guardrails
    
    Returns all the guardrails stored in the Firebase Realtime Database as a JSON response object.
    """
    
    rails = database.db.list_ids()
    return jsonify({rails}), 200

if __name__ == '__main__':
    app.run(port=3001, debug=True)


    