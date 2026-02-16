import os
import re
import tempfile
from docling.document_converter import DocumentConverter

DATABASE_PATH = "DataBase"  # change to your root folder


def fix_broken_html(table_html):
    """
    Fix malformed closing tags like <\td> → </td>
    """
    return table_html.replace("<\\", "</")


def convert_table_with_docling(table_html):
    try:
        table_html = fix_broken_html(table_html)

        # Save table to temporary HTML file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as tmp:
            tmp.write(table_html)
            tmp_path = tmp.name

        # Convert using Docling
        converter = DocumentConverter()
        result = converter.convert(tmp_path)

        markdown = result.document.export_to_markdown().strip()

        # Remove temp file
        os.remove(tmp_path)

        return markdown

    except Exception as e:
        print("❌ Table conversion failed:", e)
        return table_html  # fallback


def process_markdown_file(md_path):
    print(f"Processing: {md_path}")

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find HTML tables
    tables = re.findall(r"<table.*?>.*?</table>", content, re.DOTALL)

    if not tables:
        return

    updated_content = content

    for table in tables:
        converted_table = convert_table_with_docling(table)
        updated_content = updated_content.replace(table, converted_table)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print(f"✔ Table converted safely in: {md_path}")


def process_database():
    for root, dirs, files in os.walk(DATABASE_PATH):
        for file in files:
            if file.endswith(".md"):
                process_markdown_file(os.path.join(root, file))

    print("\n✅ All markdown files processed.")


if __name__ == "__main__":
    process_database()
