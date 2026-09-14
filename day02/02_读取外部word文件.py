from langchain_community.document_loaders import UnstructuredWordDocumentLoader

loader = UnstructuredWordDocumentLoader(
    file_path= './word.docx',
    encoding='utf-8',
    mode='elements',
)

docs = loader.load()
for doc in docs:
    print(doc.page_content, end='\n\n--------------------------------->')