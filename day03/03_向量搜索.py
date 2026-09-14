import os
import requests
from pymilvus import MilvusClient
from dotenv import load_dotenv
load_dotenv()

COLLECTION_NAME = "demo_collection"

# ==========================
# 1. 获取Embedding
# ==========================

def get_embedding(text):
    api_key = os.getenv("EMBEDDING_KEY")
    url = "https://api.siliconflow.cn/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "BAAI/bge-m3",
        "input": text
    }
    response = requests.post(
        url,
        headers=headers,
        json=data
    )

    result = response.json()
    vector = result["data"][0]["embedding"]
    print("向量维度:", len(vector))
    return vector



# ==========================
# 2. 连接Milvus
# ==========================

def get_client():
    client = MilvusClient(
        uri="http://106.55.93.112:19530",
        token=""
    )
    return client



# ==========================
# 3. 向量搜索
# ==========================

def search(client, question):
    # 生成问题向量
    vector = get_embedding(question)
    result = client.search(
        collection_name=COLLECTION_NAME,
        data=[vector],
        # 搜索哪个字段
        anns_field="vector",
        # 返回数量
        limit=5,
        search_params={
            # 你创建索引使用的是COSINE
            "metric_type":"COSINE",
            "params":{
                "ef":64
            }
        },
        output_fields=[
            "text",
            "metadata"
        ]
    )
    return result



# ==========================
# 4. 打印结果
# ==========================

def print_result(results):
    print(results, '->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    print("\n=========搜索结果=========")
    for hits in results:
        for item in hits:
            print("----------------")
            print(
                "距离:",
                item["distance"]
            )
            print(
                "文本:",
                item["entity"]["text"]
            )
            print(
                "metadata:",
                item["entity"]["metadata"]
            )

if __name__=="__main__":
    client=get_client()
    # 确保collection加载
    client.load_collection(
        COLLECTION_NAME
    )
    question="鱼为什么会游泳"
    results = search(
        client,
        question
    )
    print_result(results)