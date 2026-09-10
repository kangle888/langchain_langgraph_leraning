from docutils.utils import SystemMessage
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from pydantic import BaseModel,Field
from langchain_core.messages import HumanMessage,SystemMessage,AIMessage
load_dotenv()

llm = ChatOpenAI(
    model = "deepseek-v3.2",
    temperature=0.0,
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY")
)
# 元组
# input_tuple = [
#     ('system', '你是一个素质很低的小助手，不喜欢任何人'),
#     ('user', '你好，今天过的怎么样')
# ]

# dict
# input_tuple = [
#     {'role' : 'system', 'content' : '你是一个素质很低的小助手，不喜欢任何人' },
#     {'role' : 'user', 'content' : '你好，今天过的怎么样' }
# ]

input_message_object = [
    SystemMessage(content="你是一个小狗，只会汪汪"),
    HumanMessage(content = '吹了个口哨')
]

tuple_response = llm.invoke(
    # input_tuple
    input_message_object
)
print(tuple_response.content)


