import os
import requests
from dotenv import load_dotenv


class Database:
    def __init__(self):
        load_dotenv()
        DB_NAME = os.getenv("FIREBASE_DB")
        if not DB_NAME:
            raise ValueError("FIREBASE_DB environment variable is required")
        self.BASE_URL = f"https://{DB_NAME}-default-rtdb.europe-west1.firebasedatabase.app"
        print(f"Database initialized with base URL: {self.BASE_URL}")
        
    def clear(self):
        resp = requests.delete(f"{self.BASE_URL}/guardrails.json")
        return resp.json()
    
    def put(self, id, data):
        resp = requests.put(f"{self.BASE_URL}/guardrails/{id}.json", json=data)
        return resp.status_code, resp.json()
    
    def get(self, id):
        resp = requests.get(f"{self.BASE_URL}/guardrails/{id}.json")
        if resp.status_code == 200 and resp.json() is None:
            return 404, {"error": f"Guardrail with ID {id} not found"}
        return resp.status_code, resp.json()
    
    def delete(self, id):
        resp = requests.delete(f"{self.BASE_URL}/guardrails/{id}.json")
        return resp.status_code, resp.json()
    
    def list_ids(self):
        resp = requests.get(f"{self.BASE_URL}/guardrails.json")
        if resp.status_code == 200:
            data = resp.json()
            return list(data.keys()) if data else []
        else:
            raise Exception(f"Failed to list guardrails: {resp.status_code} - {resp.text}")
        

db = Database()