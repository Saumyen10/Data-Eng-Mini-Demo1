from dotenv import load_dotenv
import os

load_dotenv()

API_URL = os.getenv("API_URL")
FILE_URL = os.getenv("FILE_URL")
DB_URL = os.getenv("DB_URL")
REJECTED_FILE_URL = os.getenv("REJECTED_FILE_URL")


if not API_URL:
    raise ValueError("API_URL is missing or empty in .env")

if not FILE_URL:
    raise ValueError("FILE_URL is missing or empty in .env")

if not DB_URL:
    raise ValueError("DB_URL is missing or empty in .env")

if not REJECTED_FILE_URL:
    raise ValueError("REJECTED_FILE_URL is missing or empty in .env")