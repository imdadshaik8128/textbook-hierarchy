import os
import re

HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.*)')

ROOT_FOLDER = "DataBase"   # your main root folder


def extract_hierarchy(md_path):
    """
    Extract heading hierarchy from a markdown file
    """
    hierarchy_lines = []

    with open(md_path, "r", encoding="utf-8") as f:
        for line in f:
            match = HEADING_PATTERN.match(line.strip())
            if match:
                level = len(match.group(1))
                title = match.group(2)
                indent = "  " * (level - 1)
                hierarchy_lines.append(f"{indent}{'#' * level} {title}")

    return hierarchy_lines


def process_root_folder(root_folder):
    """
    Walk subject folders, extract hierarchy,
    and save hierarchy files in root folder
    """
    for subject in os.listdir(root_folder):
        subject_path = os.path.join(root_folder, subject)

        if not os.path.isdir(subject_path):
            continue

        for file in os.listdir(subject_path):
            if not file.lower().endswith(".md"):
                continue

            md_path = os.path.join(subject_path, file)

            hierarchy = extract_hierarchy(md_path)

            if not hierarchy:
                continue

            output_filename = f"{subject}__{os.path.splitext(file)[0]}_hierarchy.txt"
            output_path = os.path.join(root_folder, output_filename)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(hierarchy))

            print(f"✔ Saved hierarchy: {output_path}")


def main():
    process_root_folder(ROOT_FOLDER)
    print("\n✅ ALL HIERARCHIES EXTRACTED SUCCESSFULLY")


if __name__ == "__main__":
    main()
