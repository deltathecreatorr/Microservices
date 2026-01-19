import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

class LLMService():
    """
    Service class responsible for interacting with the Mistral LLM API.

    This class handles sending prompts to the LLM, managing requests and responses. 
    It also handles returning the generated text to the user,
    acting as an abstraction layer between the application and the underlying language model.

    Attributes:
        apiKey (str): The API key for authenticating with the Mistral LLM service.
        model (str): The specific LLM model to use for generating responses.

    Methods:
        generate_response(prompt): Sends a prompt to the LLM and returns the generated response.
    """
    
    def __init__(self, MISTRAL_API_KEY=None, model=None):
        self.apiKey = MISTRAL_API_KEY
        self.model = model  

    def generate_response(self, prompt):
        """
        Takes a prompt string as input and returns the generated response from the LLM.

        This method constructs the request payload, sends it to the Mistral LLM API,
        and processes the response to extract the generated text.
        
        Arguments:
            prompt (str): The input prompt to send to the LLM.
        
        Returns:
            content (str): The generated response from the LLM.
        """
        
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
            content = full_response["choices"][0]["message"]["content"]
            return content
        except (KeyError, IndexError) as e:
            raise Exception("Unexpected response format: " + str(full_response)) from e

llm = LLMService(MISTRAL_API_KEY=os.getenv("MISTRAL_API_KEY"), model="mistral-large-2512")    

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
    app.run(port=3000, debug=True)
