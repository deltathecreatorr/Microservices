import os
import json
from click import prompt
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

class LLMService():
    def __init__(self, MISTRAL_API_KEY=None, model=None):
        self.apiKey = MISTRAL_API_KEY
        print(f"MISTRAL_API_KEY set: {self.apiKey}")
        self.model = model  

    def generate_response(self, prompt):
        if not self.apiKey:
            raise ValueError("API key is required")
        
        headers = {
            "Authorization": f"Bearer {self.apiKey}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}]
        }

        response = requests.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=payload)

        if response.status_code != 200:
            raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
        full_response = response.json()

        try:
            content = full_response['choices'][0]['message']['content']
            return content
        except (KeyError, IndexError) as e:
            raise Exception("Unexpected response format: " + str(full_response)) from e
        
        return response.json()

llm = LLMService(MISTRAL_API_KEY=os.getenv("MISTRAL_API_KEY"), model="mistral-7b-instruct-v0.1")    

@app.route('/llm', methods=['POST'])
def llm_endpoint():
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "Missing 'prompt' in request body"}), 400
        prompt_text = data['prompt']
        print(f"Received prompt: {prompt_text}")
    except Exception as e:
        return jsonify({"error": "Invalid JSON or missing 'prompt'"}), 400
    
    try:
        output_text = llm.generate_response(prompt_text)
        print(f"Generated output: {output_text}")
        return jsonify({"output": output_text}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except ConnectionError as ce:
        return jsonify({"error": "Connection error: " + str(ce)}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    print("Starting LLM Service...")
    app.run(port=3000, debug=False)