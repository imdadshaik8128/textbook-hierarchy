import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


# ==============================
# SETTINGS
# ==============================

EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
INDEX_ROOT = "faiss_indexes"

CLASS_NAME = "Class_10"
SUBJECT_NAME = "x biology em.pdf-4f4ec816-c3f7-4ded-ac4d-b15afb44cce2"

INDEX_PATH = os.path.join(INDEX_ROOT, f"{CLASS_NAME}_{SUBJECT_NAME}")


# ==============================
# LOAD EMBEDDINGS + INDEX
# ==============================

print("🧠 Loading embedding model...")
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

print("📂 Loading subject index...")
vectorstore = FAISS.load_local(
    INDEX_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)

print("✅ Index loaded!")


# ==============================
# SIMPLE RETRIEVAL
# ==============================

def search(query, k=5):

    print(f"\n🔎 Query: {query}")

    results = vectorstore.similarity_search(query, k=k)

    print(f"\n📊 Retrieved {len(results)} results\n")

    for i, doc in enumerate(results):
        print("=" * 80)
        print(f"Result {i+1}")
        print("-" * 80)
        print(doc.page_content[:500])
        print("\nMetadata:", doc.metadata)


if __name__ == "__main__":

    search("What is the function of insulin?")
    search("Explain digestion process.")
