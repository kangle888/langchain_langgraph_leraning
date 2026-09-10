from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
load_dotenv()

llm = ChatOpenAI(
    model = "deepseek-v3.2",
    temperature=0.0,
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY")
)

response = llm.stream(
    '写一个400字的结婚农村发言稿，不要煽情'
)

for chunk in response:
    print(chunk.content, end='')