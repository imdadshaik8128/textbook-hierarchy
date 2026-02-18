import os
import re
from PIL import Image
import imagehash

# ---------------- CONFIG ----------------

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")

PHASH_THRESHOLD = 10
DHASH_THRESHOLD = 8
AHASH_THRESHOLD = 6

# --------------------------------------


def compute_hashes(image_path):
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        return {
            "phash": imagehash.phash(img),
            "dhash": imagehash.dhash(img),
            "ahash": imagehash.average_hash(img),
        }


def is_similar(h1, h2):
    return (
        h1["phash"] - h2["phash"] <= PHASH_THRESHOLD or
        h1["dhash"] - h2["dhash"] <= DHASH_THRESHOLD or
        h1["ahash"] - h2["ahash"] <= AHASH_THRESHOLD
    )

def load_reference_hashes(reference_dir):
    """
    Load hashes for ALL images inside reference_images folder
    """
    reference_hashes = []

    for file in os.listdir(reference_dir):
        if file.lower().endswith(IMAGE_EXTS):
            img_path = os.path.join(reference_dir, file)
            try:
                reference_hashes.append(compute_hashes(img_path))
            except Exception as e:
                print(f"⚠️ Skipped reference image {file}: {e}")

    return reference_hashes

# --------------------------------------------------
# STEP 1: Find similar image filenames
# --------------------------------------------------

def find_similar_images(reference_hashes, image_root):
    matched_files = set()

    for root, _, files in os.walk(image_root):
        for file in files:
            if not file.lower().endswith(IMAGE_EXTS):
                continue

            img_path = os.path.join(root, file)

            try:
                img_hashes = compute_hashes(img_path)
            except Exception as e:
                print(f"⚠️ Skipped image {img_path}: {e}")
                continue

            for ref_hash in reference_hashes:
                if is_similar(img_hashes, ref_hash):
                    matched_files.add(file)
                    break

    return matched_files



# --------------------------------------------------
# STEP 2: Insert sentence below image tag
# --------------------------------------------------

def insert_sentence_below_image(md_root, matched_images, sentence):
    img_tag_pattern = re.compile(r'!\[[^\]]*\]\(([^)]+)\)')

    for root, _, files in os.walk(md_root):
        for file in files:
            if not file.lower().endswith(".md"):
                continue

            md_path = os.path.join(root, file)

            with open(md_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            updated_lines = []
            changed = False

            for i, line in enumerate(lines):
                updated_lines.append(line)

                match = img_tag_pattern.search(line)
                if not match:
                    continue

                img_path = match.group(1)
                img_name = os.path.basename(img_path)

                if img_name in matched_images:
                    # Avoid duplicate insertion
                    if i + 1 < len(lines) and lines[i + 1].strip() == sentence.strip():
                        continue

                    updated_lines.append(sentence.rstrip() + "\n")
                    changed = True

            if changed:
                with open(md_path, "w", encoding="utf-8") as f:
                    f.writelines(updated_lines)

                print(f"✔ Updated: {md_path}")



reference_images = "reference_images"        # folder
matched_images_root = "matched_images"       # folder
DataBase = "DataBase"                         # markdown root
SENTENCE_TO_INSERT = "# Glossary"

# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():
    print("🔍 Loading reference images...")
    reference_hashes = load_reference_hashes(reference_images)

    if not reference_hashes:
        print("❌ No reference images found.")
        return

    print("🔍 Searching for similar images...")
    matched_images = find_similar_images(
        reference_hashes,
        matched_images_root
    )

    if not matched_images:
        print("❌ No similar images found.")
        return

    print("\nMatched image filenames:")
    for img in matched_images:
        print(" -", img)

    print("\n✏ Inserting sentence below image tags...")
    insert_sentence_below_image(
        md_root=DataBase,
        matched_images=matched_images,
        sentence=SENTENCE_TO_INSERT
    )

    print("\n✅ Done.")


if __name__ == "__main__":
    main()
