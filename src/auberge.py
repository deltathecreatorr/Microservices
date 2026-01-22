
import requests
import re
from flask import Flask, request, jsonify

app = Flask(__name__)

GUARDRAILS_API_URL = "http://localhost:3001/guardrails"
LLM_API_URL = "http://localhost:3000/llm"

def get_guardrails():
    """
    Handles gathering all of the guardrails from the DB
    
    Returns a list of guardrail IDS using the List Guardrails endpoint
    of the Guardrails microservice.
    """
    guardrails = []
    try:
        response = requests.get(f"{GUARDRAILS_API_URL}")
        if response.status_code == 200:
            guardrails_ids = response.json()

            if not guardrails_ids:
                return guardrails
            
            for gid in guardrails_ids:
                guardrail = requests.get(f"{GUARDRAILS_API_URL}/{gid}")
                if guardrail.status_code == 200:
                    guardrails.append(guardrail.json())
        return guardrails
    except Exception as e:
        print(f"Error fetching guardrails: {e}")
        return guardrails
    
def sanitise_text(text, guardrails):
    """
    Handles the sanitation of text from the inputs and outputs of the LLM
    
    Arguments:
        text (str): The text to be sanitised
        guardrails (list): A list of guardrail dictionaries

    Returns:
        sanitised_text (str): The sanitised text
    """
    
    if not text:
        return ""
    
    sanitised_text = text

    for rail in guardrails:
        try:
            regx = rail.get("regx")
            substitution = rail.get("sub")

            if regx and substitution is not None:
                sanitised_text = re.sub(regx, substitution, sanitised_text)
        except re.error as re_err:
            print(f"Invalid regex '{regx}' in guardrail ID '{rail.get('id')}': {re_err}")
            continue
    return sanitised_text

@app.route('/auberge', methods=['POST'])
def auberge():
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "Missing 'prompt' in request body"}), 400
        prompt = data['prompt']

        active_guardrails = get_guardrails()
        sanitised_prompt = sanitise_text(prompt, active_guardrails)

        llm_payload = {"prompt": sanitised_prompt}
        llm_response = requests.post(LLM_API_URL, json=llm_payload)

        if llm_response.status_code == 200:
            llm_output = llm_response.json().get("output", "")
            sanitised_output = sanitise_text(llm_output, active_guardrails)
            return jsonify({"output": sanitised_output}), 200
        else:
            return jsonify({"error": "LLM service error", "details": llm_response.text}), llm_response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=3002, debug=True)
    