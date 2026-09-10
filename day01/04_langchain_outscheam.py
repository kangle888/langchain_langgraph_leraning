from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from pydantic import BaseModel,Field
load_dotenv()

llm = ChatOpenAI(
    model = "deepseek-v3.2",
    temperature=0.0,
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY")
)

class CalendarEvent(BaseModel):
    name : str
    date : str
    participants : list[str]


#3、使用with_structured_output，得到一个新的llm，用于生成结构化输出
new_llm=llm.with_structured_output(schema=CalendarEvent)
#4、调用新的llm，生成结构化输出
res=new_llm.invoke("Alice and Bob are going to a sciencefair onFriday.")
print(res)
print(type(res))