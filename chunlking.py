import os
import re
from pathlib import Path
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_core.documents import Document

DATABASE_PATH = "database"

# Keywords to detect exercise sections
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


# ---------------------------------------------------
# IMAGE HANDLING
# ---------------------------------------------------

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


# ---------------------------------------------------
# CONTENT TYPE DETECTION
# ---------------------------------------------------

def detect_content_type(metadata):
    combined_text = ""

    for key in ["chapter", "section", "subsection"]:
        if key in metadata:
            combined_text += metadata[key].lower() + " "

    if any(keyword in combined_text for keyword in EXERCISE_KEYWORDS):
        return "exercise"

    return "theory"


# ---------------------------------------------------
# MARKDOWN CHUNKING
# ---------------------------------------------------

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

        # Remove image markdown from text
        clean_text = remove_image_markdown(doc.page_content)

        # Detect content type
        content_type = detect_content_type(doc.metadata)

        # Build metadata
        metadata = doc.metadata.copy()

        metadata.update({
            "class": class_name,
            "subject": subject_name,
            "images": images,
            "content_type": content_type,
            "source_file": str(file_path)
        })

        processed_docs.append(
            Document(
                page_content=clean_text.strip(),
                metadata=metadata
            )
        )

    return processed_docs


# ---------------------------------------------------
# PROCESS ENTIRE DATABASE
# ---------------------------------------------------

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


# ---------------------------------------------------
# OPTIONAL: DEBUG SAVE
# ---------------------------------------------------

import json

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


# ---------------------------------------------------
# MAIN
# ---------------------------------------------------

if __name__ == "__main__":
    documents = process_database()
    save_chunks_to_json(documents)
