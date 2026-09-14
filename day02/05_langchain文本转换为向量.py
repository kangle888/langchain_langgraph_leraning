from langchain_huggingface import HuggingFaceEmbeddings

def embedding_demo():
    embed_model= HuggingFaceEmbeddings(
        model_name=r'.\assets\models\bge-base-zh-v1.5'
    )
    #单文本嵌入
    query="你好，世界"
    query_result=embed_model.embed_query(query)
    print(len(query_result))
    print(query_result[0:10])
    #多文本嵌入
    docs=["你好，世界","你好，世界"]
    res=embed_model.embed_documents(docs)
    print(type(res))

if __name__=="__main__":
    embedding_demo()