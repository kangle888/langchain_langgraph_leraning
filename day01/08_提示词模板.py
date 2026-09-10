from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
load_dotenv()

chat_prompt_template = ChatPromptTemplate.from_messages(
    messages=[
        ("system", "你是一个专业的评论员"),
        ("human", "请评价{product}的优缺点，包括{aspect1}和{aspect2}。"),
    ]
)

prompt = chat_prompt_template.invoke(
    {"product":"iPhone15","aspect1":"性能","aspect2":"外观"}
)

llm = ChatOpenAI(
    model="deepseek-v3.2",
    base_url=os.getenv("OPENAI_API_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
)

response = llm.invoke(prompt)
print(response)