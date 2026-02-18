import json
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

def load_documents_from_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = []

    for item in data:
        documents.append(
            Document(
                page_content=item["text"],
                metadata=item["metadata"]
            )
        )

    return documents

def build_index_from_json(json_path):

    documents = load_documents_from_json(json_path)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.from_documents(
        documents,
        embeddings
    )

    vectorstore.save_local("faiss_index")

    print("✅ FAISS index created from JSON")

if __name__ == "__main__":

    build_index_from_json("chunks_debug.json")