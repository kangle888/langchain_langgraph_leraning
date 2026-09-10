import os
from dotenv import load_dotenv
load_dotenv()
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel,Field
llm = ChatOpenAI(
    model="deepseek-v3.2",
    temperature=0.0,
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY")
)

class Prime(BaseModel):
    prime:list[int]=Field(description="素数")
    count:list[int]=Field(description="小于该素数的素数个数")

json_parser=JsonOutputParser(pydantic_object=Prime)

print(json_parser.get_format_instructions())
res=llm.invoke(
    [
        ("system",json_parser.get_format_instructions()),
        ("user","任意生成5个1000-100000之间素数，并标出小于该素数的素数个数")
    ])
print('********************************************')
print(res.content)
print('********************************************')
parsed_res=json_parser.invoke(res)
print('********************************************')
print(type(parsed_res))
print('*****************11111111111111***************************')
print(parsed_res)