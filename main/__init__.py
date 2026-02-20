from flask import Flask
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'downloads')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

from main import routes  # ملف routes.py يحتوي على الدوال