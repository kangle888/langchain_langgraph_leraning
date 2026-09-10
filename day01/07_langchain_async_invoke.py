from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
load_dotenv()



async  def async_invoke():
    llm = ChatOpenAI(
        model="deepseek-v3.2",
        api_key=os.getenv("API_KEY"),
        api_secret=os.getenv("API_SECRET"),
    )
    response = await llm.invoke('你好')
    print(response)