from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
import os
load_dotenv()


client = MultiServerMCPClient(
    {
        "12306-mcp":
        {
            "transport": "streamable_http",
            "url": "https://mcp.api-inference.modelscope.net/de957c333f4e43/mcp"
        }
    }
)

async def mian():
    tools = await client.get_tools()
    # print(tools)
    llm = ChatOpenAI(
        model="deepseek-v3.2",
        temperature=0.0,
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY")
    )
    agent = create_agent(
        llm,
        tools
    )
    response = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "查询一下9月深圳到武汉的火车票"
                }
            ]
        }
    )
    print(response)

if __name__ == "__main__":
   import  asyncio
   asyncio.run(mian())