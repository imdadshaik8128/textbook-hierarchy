import os
import shutil
from PIL import Image
import imagehash

# ---------------- CONFIG ----------------

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")

# Similarity thresholds (SAFE DEFAULTS)
PHASH_THRESHOLD = 10
DHASH_THRESHOLD = 8
AHASH_THRESHOLD = 6

# ----------------------------------------


def compute_hashes(image_path):
    """
    Compute multiple perceptual hashes for an image.
    """
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        return {
            "phash": imagehash.phash(img),
            "dhash": imagehash.dhash(img),
            "ahash": imagehash.average_hash(img),
        }


def load_reference_hashes(reference_dir):
    """
    Load hashes for all reference images.
    """
    reference_hashes = []

    for file in os.listdir(reference_dir):
        if file.lower().endswith(IMAGE_EXTS):
            path = os.path.join(reference_dir, file)
            try:
                reference_hashes.append(compute_hashes(path))
            except Exception as e:
                print(f"⚠️ Skipped reference image {file}: {e}")

    return reference_hashes


def is_similar(image_hashes, reference_hashes):
    """
    Check similarity using multi-hash logic.
    Match if ANY hash type is within threshold.
    """
    for ref in reference_hashes:
        if (
            image_hashes["phash"] - ref["phash"] <= PHASH_THRESHOLD
            or image_hashes["dhash"] - ref["dhash"] <= DHASH_THRESHOLD
            or image_hashes["ahash"] - ref["ahash"] <= AHASH_THRESHOLD
        ):
            return True
    return False


def move_matching_images(
    textbook_root,
    reference_hashes,
    output_dir,
    dry_run=True
):
    """
    Scan textbook_root and move matching images.
    """
    os.makedirs(output_dir, exist_ok=True)

    for root, _, files in os.walk(textbook_root):
        for file in files:
            if not file.lower().endswith(IMAGE_EXTS):
                continue

            image_path = os.path.join(root, file)

            try:
                img_hashes = compute_hashes(image_path)
            except Exception as e:
                print(f"⚠️ Skipped unreadable image {image_path}: {e}")
                continue

            if is_similar(img_hashes, reference_hashes):
                parent_folder = os.path.basename(root)
                new_name = f"{parent_folder}__{file}"
                dest_path = os.path.join(output_dir, new_name)

                if dry_run:
                    print(f"[DRY RUN] MATCH FOUND → {image_path}")
                else:
                    shutil.move(image_path, dest_path)
                    print(f"✔ MOVED → {dest_path}")


def main():
    reference_dir = "reference_images"
    textbook_root = "DataBase"
    output_dir = "matched_images"

    print("Loading reference image hashes...")
    reference_hashes = load_reference_hashes(reference_dir)

    if not reference_hashes:
        print("❌ No reference images loaded. Exiting.")
        return

    print("Scanning textbook images...\n")

    # FIRST RUN MUST BE DRY RUN
    move_matching_images(
        textbook_root=textbook_root,
        reference_hashes=reference_hashes,
        output_dir=output_dir,
        dry_run=False   # 🔒 CHANGE TO False AFTER VERIFYING
    )


if __name__ == "__main__":
    main()
