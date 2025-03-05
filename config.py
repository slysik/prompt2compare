import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
PROMPTLAYER_API_KEY = os.getenv("PROMPTLAYER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# App Config
PORT = 9999