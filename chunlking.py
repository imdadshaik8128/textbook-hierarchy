import os
import re
import uuid
import json
from pathlib import Path
from bs4 import BeautifulSoup

from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_core.documents import Document


DATABASE_PATH = "DataBase"


# =====================================================
# EXERCISE KEYWORDS
# =====================================================

EXERCISE_KEYWORDS = [
    "exercise",
    "exercises",
    "improve your learning",
    "fill in the blanks",
    "choose the correct answer",
    "write in brief",
    "discuss",
    "project",
    "questions",
    "what you have learnt",
    "group activity",
]


# =====================================================
# IMAGE HANDLING
# =====================================================

def extract_images(text, class_name, subject_name):
    pattern = r'!\[.*?\]\((.*?)\)'
    images = re.findall(pattern, text)

    fixed_images = []
    for img in images:
        fixed_images.append(
            f"{class_name}/{subject_name}/{img}"
        )

    return fixed_images


def remove_image_markdown(text):
    return re.sub(r'!\[.*?\]\((.*?)\)', '', text)


# =====================================================
# CONTENT TYPE DETECTION
# =====================================================

def detect_content_type(metadata):
    combined_text = ""

    for key in ["chapter", "section", "subsection"]:
        if key in metadata:
            combined_text += metadata[key].lower() + " "

    if any(keyword in combined_text for keyword in EXERCISE_KEYWORDS):
        return "exercise"

    return "theory"


# =====================================================
# HTML TABLE PROCESSING
# =====================================================

def html_table_to_documents(
    html_text,
    class_name,
    subject_name,
    base_metadata,
    rows_per_chunk=8
):
    soup = BeautifulSoup(html_text, "html.parser")
    documents = []

    tables = soup.find_all("table")

    if not tables:
        return []

    for table in tables:

        original_html_table = str(table)

        header_row = table.find("tr")
        headers = []

        if header_row:
            headers = [
                cell.get_text(strip=True)
                for cell in header_row.find_all(["th", "td"])
            ]

        rows = table.find_all("tr")[1:]

        row_sentences = []

        for row in rows:
            cells = [
                cell.get_text(strip=True)
                for cell in row.find_all(["td", "th"])
            ]

            if len(cells) < len(headers):
                cells.extend(["Not specified"] * (len(headers) - len(cells)))
            elif len(cells) > len(headers):
                cells = cells[:len(headers)]

            parts = []
            for header, cell in zip(headers, cells):
                value = cell if cell else "Not specified"
                parts.append(f"{header}: {value}")

            row_sentences.append(". ".join(parts) + ".")

        table_id = str(uuid.uuid4())

        for i in range(0, len(row_sentences), rows_per_chunk):

            chunk_block = "\n".join(row_sentences[i:i + rows_per_chunk])

            structured_text = (
                f"Table Columns: {', '.join(headers)}.\n"
                f"{chunk_block}"
            )

            metadata = base_metadata.copy()
            metadata.update({
                "class": class_name,
                "subject": subject_name,
                "contains_table": True,
                "table_chunk": True,
                "table_id": table_id,
                "original_html_table": original_html_table
            })

            documents.append(
                Document(
                    page_content=structured_text.strip(),
                    metadata=metadata
                )
            )

    return documents


# =====================================================
# MARKDOWN PROCESSING
# =====================================================

def process_markdown_file(file_path, class_name, subject_name):

    with open(file_path, "r", encoding="utf-8") as f:
        markdown_text = f.read()

    headers_to_split_on = [
        ("#", "chapter"),
        ("##", "section"),
        ("###", "subsection"),
    ]

    splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
    docs = splitter.split_text(markdown_text)

    processed_docs = []

    for doc in docs:

        # Extract images
        images = extract_images(
            doc.page_content,
            class_name,
            subject_name
        )

        # Remove image markdown
        clean_text = remove_image_markdown(doc.page_content)

        # Detect exercise/theory
        content_type = detect_content_type(doc.metadata)

        # Try HTML table conversion
        table_docs = html_table_to_documents(
            html_text=clean_text,
            class_name=class_name,
            subject_name=subject_name,
            base_metadata=doc.metadata,
            rows_per_chunk=8
        )

        if table_docs:
            for table_doc in table_docs:
                table_doc.metadata.update({
                    "images": images,
                    "content_type": content_type,
                    "source_file": str(file_path)
                })

            processed_docs.extend(table_docs)
            continue

        # Normal text chunk
        metadata = doc.metadata.copy()
        metadata.update({
            "class": class_name,
            "subject": subject_name,
            "images": images,
            "content_type": content_type,
            "contains_table": False,
            "table_chunk": False,
            "source_file": str(file_path)
        })

        processed_docs.append(
            Document(
                page_content=clean_text.strip(),
                metadata=metadata
            )
        )

    return processed_docs


# =====================================================
# PROCESS DATABASE
# =====================================================

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
                        file_path,
                        class_name=class_folder,
                        subject_name=subject_folder
                    )

                    all_documents.extend(docs)

    print(f"\n✅ Total chunks created: {len(all_documents)}")
    return all_documents


# =====================================================
# DEBUG SAVE
# =====================================================

def save_chunks_to_json(docs, output_file="chunks_debug.json"):

    data = []

    for doc in docs:
        data.append({
            "text": doc.page_content,
            "metadata": doc.metadata
        })

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"📁 Saved debug file to {output_file}")


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    documents = process_database()
    save_chunks_to_json(documents)
