from pymilvus import MilvusClient, DataType

def get_milvus_client():
    client = MilvusClient(
        uri="http://106.55.93.112:19530",
        token="",
    )
    res = client.list_collections()
    print(res)
    return client

def build_schema():
    return (
        MilvusClient.create_schema(
            # 自动为id字段赋值
            auto_id=True,
        )
        # 添加id字段，类型为整数，设置为主键
        .add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
        # 添加vector字段，类型为浮点数向量，维度为1024
        .add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR,
                   dim=1024)
        # 添加text字段，类型为字符串，最大长度为1500
        .add_field(field_name="text", datatype=DataType.VARCHAR,
                   max_length=1500)
        # 添加metadata字段，类型为JSON
        .add_field(field_name="metadata", datatype=DataType.JSON)
        .add_field(field_name="sparse_vector", datatype=DataType.SPARSE_FLOAT_VECTOR)
    )

def build_index():
    index_params=MilvusClient.prepare_index_params()
    index_params.add_index(
        field_name="vector",#建立索引的字段
        index_type="HNSW",#索引类型
        metric_type="L2",#向量相似度度量方式
    )
    index_params.add_index(
        field_name="sparse_vector",
        index_type="SPARSE_INVERTED_INDEX",
        metric_type="IP",
    )
    return index_params

def create_collection(client):
    client.drop_collection(collection_name="demo_collection")
    if not client.has_collection(collection_name="demo_collection"):
        print("collection demo_collection not exists, create it")
        client.create_collection(
            collection_name="demo_collection",  # collection名称
            schema=build_schema(),  # collection的schema
            index_params=build_index(),  # collection的index
        )
        # 查看collection
        print(client.list_collections())
        # 查看collection描述
        print(client.describe_collection(collection_name="demo_collection"))

if __name__ == '__main__':
    create_collection(get_milvus_client())