from langchain_unstructured import UnstructuredLoader

try:
    loader = UnstructuredLoader(
        file_path="./fish.md",
        mode="single"
    )
    docs = loader.load()
    for doc in docs:
        print(doc.page_content)
        print("\n==============================")

except Exception as e:
    print(f"发生错误: {e}")