import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(
    base_url = os.getenv("OPENAI_API_URL"),
    api_key = os.getenv("OPENAI_API_KEY"),
)

response = client.chat.completions.create(
    model = "deepseek-v3.2",
    messages=[{"role":"user","content":"将'你好'翻译成意大利语"}],
)
print(response)