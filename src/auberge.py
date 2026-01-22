
import requests
from flask import Flask, request, app

app = Flask(__name__)

@app.route('/auberge', methods=['GET'])
def auberge():
    pass