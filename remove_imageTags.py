
import os
import re

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")
MATCHED_IMAGES_DIR = "matched_images"
MARKDOWN_ROOT = "DataBase"

def load_matched_image_names(matched_dir):
    return {
        f.split("__")[-1]   # handle biology__img.png → img.png
        for f in os.listdir(matched_dir)
        if f.lower().endswith(IMAGE_EXTS)
    }

def remove_image_tags(md_root, matched_images):
    img_tag_pattern = re.compile(r'!\[[^\]]*\]\(([^)]+)\)')

    for root, _, files in os.walk(md_root):
        for file in files:
            if file.lower() != "full_cleaned.md":
                continue

            md_path = os.path.join(root, file)

            with open(md_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            new_lines = []
            removed = False

            for line in lines:
                match = img_tag_pattern.search(line)
                if match:
                    img_name = os.path.basename(match.group(1))
                    if img_name in matched_images:
                        removed = True
                        continue  # ❌ remove this line

                new_lines.append(line)

            if removed:
                with open(md_path, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)

                print(f"✔ Removed image tags from: {md_path}")


def clean_before_chapter_one(md_root):
    img_tag_pattern = re.compile(r'!\[[^\]]*\]\(([^)]+)\)')

    for root, _, files in os.walk(md_root):
        for file in files:
            if file.lower() != "full_cleaned.md":
                continue

            md_path = os.path.join(root, file)

            with open(md_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            chapter_index = None
            images_to_delete = set()

            for i, line in enumerate(lines):
                if line.strip().lower() == "# chapter 1":
                    chapter_index = i
                    break

                match = img_tag_pattern.search(line)
                if match:
                    images_to_delete.add(os.path.basename(match.group(1)))

            if chapter_index is None:
                continue

            # Remove everything above Chapter 1
            cleaned_lines = lines[chapter_index:]

            with open(md_path, "w", encoding="utf-8") as f:
                f.writelines(cleaned_lines)

            print(f"✔ Cleaned content above Chapter 1 in: {md_path}")

            # Delete images from SAME folder
            for img in images_to_delete:
                img_path = os.path.join(root, img)
                if os.path.exists(img_path):
                    try:
                        os.remove(img_path)
                        print(f"🗑 Deleted image: {img_path}")
                    except Exception as e:
                        print(f"⚠️ Failed to delete {img_path}: {e}")

def main():
    print("🔹 Loading matched image names...")
    matched_images = load_matched_image_names(MATCHED_IMAGES_DIR)

    print("\n✂ STEP 1: Removing matched image tags...")
    remove_image_tags(
        md_root=MARKDOWN_ROOT,
        matched_images=matched_images
    )

    print("\n🧹 STEP 2: Cleaning content above '# Chapter 1'...")
    clean_before_chapter_one(
        md_root=MARKDOWN_ROOT
    )

    print("\n✅ DONE.")


if __name__ == "__main__":
    main()
