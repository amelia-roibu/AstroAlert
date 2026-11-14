import os
from dotenv import load_dotenv

load_dotenv() # citeste fisierul .env

NASA_API_KEY = os.getenv("NASA_API_KEY")
NASA_API_URL = "https://api.nasa.gov/neo/rest/v1/feed"