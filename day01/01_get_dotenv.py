import os
from dotenv import load_dotenv
load_dotenv()

base_url = os.getenv("OPENAI_BASE_URL")
print(base_url)
api_key = os.getenv("OPENAI_API_KEY")
print(api_key)