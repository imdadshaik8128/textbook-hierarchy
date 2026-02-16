import os
from pypdf import PdfReader, PdfWriter

INPUT_DIR = "input_pdfs"      # folder with original PDFs
OUTPUT_DIR = "output"

ODD_DIR = os.path.join(OUTPUT_DIR, "odd_pages")
EVEN_DIR = os.path.join(OUTPUT_DIR, "even_pages")

os.makedirs(ODD_DIR, exist_ok=True)
os.makedirs(EVEN_DIR, exist_ok=True)

for filename in os.listdir(INPUT_DIR):
    if not filename.lower().endswith(".pdf"):
        continue

    input_path = os.path.join(INPUT_DIR, filename)
    base_name = os.path.splitext(filename)[0]

    odd_output_path = os.path.join(
        ODD_DIR, f"{base_name}_odd_pages.pdf"
    )
    even_output_path = os.path.join(
        EVEN_DIR, f"{base_name}_even_pages.pdf"
    )

    reader = PdfReader(input_path)
    odd_writer = PdfWriter()
    even_writer = PdfWriter()

    for page_number, page in enumerate(reader.pages, start=1):
        if page_number % 2 == 0:
            even_writer.add_page(page)
        else:
            odd_writer.add_page(page)

    if odd_writer.pages:
        with open(odd_output_path, "wb") as f:
            odd_writer.write(f)

    if even_writer.pages:
        with open(even_output_path, "wb") as f:
            even_writer.write(f)

    print(f"Processed: {filename}")

print("\n✅ Batch processing completed.")
