from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import requests
import os
from dotenv import load_dotenv
from pymilvus import MilvusClient, DataType

load_dotenv()

COLLECTION_NAME = "demo_collection"

# 获取Embedding向量
def get_embedding(text):
    API_KEY = os.getenv("EMBEDDING_KEY")
    url = "https://api.siliconflow.cn/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
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
    return result["data"][0]["embedding"]


# 连接Milvus
def get_milvus_client():
    client = MilvusClient(
        uri="http://106.55.93.112:19530",
        token=""
    )
    print("当前collection:", client.list_collections())
    return client

# 创建Schema
def build_schema():
    schema = MilvusClient.create_schema(
        auto_id=True
    )
    schema.add_field(
        field_name="id",
        datatype=DataType.INT64,
        is_primary=True
    )
    # bge-m3 默认1024维
    schema.add_field(
        field_name="vector",
        datatype=DataType.FLOAT_VECTOR,
        dim=1024
    )

    schema.add_field(
        field_name="text",
        datatype=DataType.VARCHAR,
        max_length=1500
    )

    schema.add_field(
        field_name="metadata",
        datatype=DataType.JSON
    )
    return schema


# 创建索引
def build_index():
    index_params = MilvusClient.prepare_index_params()
    index_params.add_index(
        field_name="vector",
        index_type="HNSW",
        metric_type="COSINE"
    )
    return index_params


# 创建Collection
def create_collection(client):
    if client.has_collection(COLLECTION_NAME):
        print("collection已经存在")
        return
    print("创建collection...")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        schema=build_schema(),
        index_params=build_index()
    )
    print(client.describe_collection(collection_name=COLLECTION_NAME))


# 加载文件并切割
def load_documents():
    loader = UnstructuredLoader(
        file_path="./fish.md",
        encoding="utf-8",
        mode="single"
    )
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=150,
        chunk_overlap=20,
        separators=[
            "\n\n",
            "\n",
            "。",
            "！",
            "？",
            "……",
            "，",
            ""
        ]
    )
    split_docs = splitter.split_documents(docs)
    return split_docs


# 插入数据
def insert_data(client, docs):
    insert_list = []
    for doc in docs:
        text = doc.page_content
        vector = get_embedding(text)
        insert_list.append({
            "vector": vector,
            "text": text,
            "metadata": doc.metadata
        })
        print("向量维度:",len(vector))

    result = client.insert(
        collection_name=COLLECTION_NAME,
        data=insert_list
    )
    print("插入结果:")
    print(result)


if __name__ == "__main__":
    client = get_milvus_client()
    # 创建集合
    create_collection(client)
    # 加载文档
    docs = load_documents()
    print("切割数量:",len(docs))
    # 插入向量数据库
    insert_data(client,docs)
    # 加载collection
    client.load_collection(COLLECTION_NAME)
    print("Milvus数据写入完成")