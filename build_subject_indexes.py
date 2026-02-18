import os
from collections import defaultdict

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from chunlking import process_database


# ===================================
# SETTINGS
# ===================================

EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
INDEX_ROOT = "faiss_indexes"


# ===================================
# BUILD SEPARATE INDEXES
# ===================================

def build_separate_indexes():

    print("📚 Loading documents...")
    documents = process_database()

    # Group documents by (class, subject)
    grouped_docs = defaultdict(list)

    for doc in documents:
        class_name = doc.metadata.get("class")
        subject_name = doc.metadata.get("subject")

        key = f"{class_name}_{subject_name}"
        grouped_docs[key].append(doc)

    print(f"📊 Found {len(grouped_docs)} subject groups")

    print("🧠 Loading embedding model...")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    os.makedirs(INDEX_ROOT, exist_ok=True)

    # Create separate index per subject
    for group_name, docs in grouped_docs.items():

        print(f"\n🔎 Building index for {group_name}")
        print(f"   → {len(docs)} documents")

        vectorstore = FAISS.from_documents(
            docs,
            embeddings
        )

        save_path = os.path.join(INDEX_ROOT, group_name)
        vectorstore.save_local(save_path)

        print(f"   ✅ Saved to {save_path}")

    print("\n🎉 All subject indexes created successfully!")


if __name__ == "__main__":
    build_separate_indexes()
