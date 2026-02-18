import os
import cv2
import re


DATABASE_PATH = "database"  # Change if needed


def contains_qr(image_path):
    try:
        img = cv2.imread(image_path)
        if img is None:
            return False

        detector = cv2.QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(img)

        if bbox is not None and data:
            return True
        return False

    except Exception as e:
        return False



def remove_image_name_from_md(md_path, image_name):
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    updated_lines = []
    for line in lines:
        if image_name not in line:
            updated_lines.append(line)

    with open(md_path, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)


def process_books():
    for book_folder in os.listdir(DATABASE_PATH):
        book_path = os.path.join(DATABASE_PATH, book_folder)

        if not os.path.isdir(book_path):
            continue

        print(f"\nProcessing book: {book_folder}")

        # Find markdown file
        md_file = None
        for file in os.listdir(book_path):
            if file.endswith(".md"):
                md_file = os.path.join(book_path, file)
                break

        if md_file is None:
            print("No markdown file found. Skipping.")
            continue

        # Images folder
        images_folder = os.path.join(book_path, "images")
        if not os.path.exists(images_folder):
            print("No images folder found. Skipping.")
            continue

        # Scan images
        for image_name in os.listdir(images_folder):
            if image_name.lower().endswith((".png", ".jpg", ".jpeg")):
                image_path = os.path.join(images_folder, image_name)

                if contains_qr(image_path):
                    print(f"QR found: {image_name}")

                    # Delete image
                    os.remove(image_path)
                    print(f"Deleted image: {image_name}")

                    # Remove reference from markdown
                    remove_image_name_from_md(md_file, image_name)
                    print(f"Removed '{image_name}' from markdown")

    print("\n✅ QR cleaning completed.")


if __name__ == "__main__":
    process_books()
    
