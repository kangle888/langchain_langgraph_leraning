import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_core.output_parsers import StrOutputParser
load_dotenv()


llm = ChatOpenAI(
    model="deepseek-v3.2",
    base_url=os.getenv("OPENAI_API_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
)


english_chain=(
  PromptTemplate.from_template("把这个句子{topic}翻译成英文") | llm | StrOutputParser()
)
korean_chain=(
        PromptTemplate.from_template("把这个句子{topic}翻译成韩文") | llm | StrOutputParser()
)

map_chain= RunnableParallel(english=english_chain, korean=korean_chain)

response = map_chain.invoke({'topic': '我爱中国'})
print(response)