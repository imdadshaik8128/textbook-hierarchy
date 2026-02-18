import os
import re
import uuid
import json
from pathlib import Path

from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_core.documents import Document


DATABASE_PATH = "database"


# ===============================
# TABLE REPLACEMENT FUNCTION
# ===============================

def replace_markdown_table_with_text(
    text,
    class_name,
    subject_name,
    base_metadata,
    rows_per_chunk=8
):
    pattern = r'(\|.*?\|\n\|[-\s|]+\|\n(?:\|.*?\|\n?)*)'

    matches = re.finditer(pattern, text, re.DOTALL)
    documents = []

    for match in matches:
        table_block = match.group(0)
        lines = table_block.strip().split("\n")

        if len(lines) < 3:
            continue

        headers = [h.strip() for h in lines[0].strip('|').split('|')]
        row_sentences = []

        for row in lines[2:]:
            cells = [c.strip() for c in row.strip('|').split('|')]

            row_parts = []
            for header, cell in zip(headers, cells):
                value = cell if cell else "Not specified"
                row_parts.append(f"{header}: {value}")

            row_sentences.append(". ".join(row_parts) + ".")

        table_id = str(uuid.uuid4())

        for i in range(0, len(row_sentences), rows_per_chunk):
            chunk_block = "\n".join(row_sentences[i:i + rows_per_chunk])

            table_context = (
                f"Table Columns: {', '.join(headers)}.\n"
                f"{chunk_block}"
            )

            metadata = base_metadata.copy()
            metadata.update({
                "class": class_name,
                "subject": subject_name,
                "contains_table": True,
                "table_chunk": True,
                "table_id": table_id
            })

            documents.append(
                Document(
                    page_content=table_context.strip(),
                    metadata=metadata
                )
            )

    return documents


# ===============================
# MARKDOWN PROCESSING
# ===============================

def process_markdown_file(file_path, class_name, subject_name):
    with open(file_path, "r", encoding="utf-8") as f:
        markdown_text = f.read()

    headers_to_split_on = [
        ("#", "chapter"),
        ("##", "section"),
        ("###", "subsection"),
    ]

    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    docs = splitter.split_text(markdown_text)

    processed_docs = []

    for doc in docs:

        # 1️⃣ Try table extraction first
        table_docs = replace_markdown_table_with_text(
            text=doc.page_content,
            class_name=class_name,
            subject_name=subject_name,
            base_metadata=doc.metadata,
            rows_per_chunk=8
        )

        if table_docs:
            processed_docs.extend(table_docs)
            continue  # Skip adding original chunk if table found

        # 2️⃣ Normal text chunk
        metadata = doc.metadata.copy()
        metadata.update({
            "class": class_name,
            "subject": subject_name,
            "contains_table": False,
            "table_chunk": False
        })

        processed_docs.append(
            Document(
                page_content=doc.page_content.strip(),
                metadata=metadata
            )
        )

    return processed_docs


# ===============================
# PROCESS ENTIRE DATABASE
# ===============================

def process_database():
    all_documents = []

    for class_folder in os.listdir(DATABASE_PATH):
        class_path = os.path.join(DATABASE_PATH, class_folder)

        if not os.path.isdir(class_path):
            continue

        for subject_folder in os.listdir(class_path):
            subject_path = os.path.join(class_path, subject_folder)

            if not os.path.isdir(subject_path):
                continue

            for file in os.listdir(subject_path):
                if file.endswith(".md"):
                    file_path = os.path.join(subject_path, file)

                    docs = process_markdown_file(
                        file_path=file_path,
                        class_name=class_folder,
                        subject_name=subject_folder
                    )

                    all_documents.extend(docs)

    print(f"\n✅ Total chunks created: {len(all_documents)}")
    return all_documents


# ===============================
# DEBUG SAVE
# ===============================

def save_chunks_to_json(docs):
    data = []

    for doc in docs:
        data.append({
            "text": doc.page_content,
            "metadata": doc.metadata
        })

    with open("chunks_debug.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print("✅ Saved chunks_debug.json")


# ===============================
# MAIN ENTRY
# ===============================

if __name__ == "__main__":
    documents = process_database()
    save_chunks_to_json(documents)
