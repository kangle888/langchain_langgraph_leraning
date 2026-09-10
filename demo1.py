from langchain.chat_models import init_chat_model

model = init_chat_model(
    model="deepseek-v3.2",
    model_provider = "openai",
    api_key = "sk-077482897415462dba6706ad0fffd7a9",
    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

response = model.invoke('你是谁？')

print(response)