import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv('DB_URL')

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
