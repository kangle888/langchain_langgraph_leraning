from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
load_dotenv()

prompt_template = PromptTemplate(
    template = "讲一个{topic}的笑话",
    input_variables = ['topic']
)

llm = ChatOpenAI(
    model="deepseek-v3.2",
    base_url=os.getenv("OPENAI_API_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
)

# 输出解析器
paser = StrOutputParser()

# 构建链接
chain = prompt_template | llm | paser

resp = chain.invoke({'topic': '人工智能'})
print(resp)