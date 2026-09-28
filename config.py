import os
from dotenv import load_dotenv

URL= "https://www.python.org/jobs/"
OUTPUT_FILE = "data/jobs.json"



load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "gemini-2.5-flash")
AI_EMBEDDING_MODEL = os.getenv("AI_EMBEDDING_MODEL", "gemini-embedding-001")