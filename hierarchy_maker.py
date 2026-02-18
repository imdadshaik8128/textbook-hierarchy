import re

ACTIVITY_KW = ["activity", "lab activity", "experiment", "practical"]
QUESTION_KW = ["exercises", "improve your learning", "group activities"]
SPECIAL_KW = [
    "do you know",
    "think and discuss",
    "key words",
    "keywords",
    "glossary",
    "summary"
]

def normalize_markdown(lines):
    output = []
    inside_chapter = False
    expecting_chapter_name = False

    for line in lines:
        stripped = line.strip()

        # ---------------- HEADINGS ----------------
        if stripped.startswith("#"):
            text = stripped.lstrip("#").strip()

            # GLOBAL SECTION
            if text.lower() == "suggested pedagogical processes":
                inside_chapter = False
                output.append("# " + text + "\n")
                continue

            # CHAPTER MARKER
            if re.match(r"chapter\s+\d+", text.lower()):
                inside_chapter = True
                expecting_chapter_name = True
                output.append("# " + text + "\n")
                continue

            # CHAPTER NAME
            if expecting_chapter_name:
                output.append("# " + text + "\n")
                expecting_chapter_name = False
                continue

            # ---------------- INSIDE CHAPTER ----------------
            if inside_chapter:

                # Number-based hierarchy
                num_match = re.match(r"(\d+(\.\d+)+)", text)
                if num_match:
                    depth = min(num_match.group(1).count(".") + 2, 4)
                    output.append("#" * depth + " " + text + "\n")
                    continue

                # Activities / Labs
                if any(k in text.lower() for k in ACTIVITY_KW):
                    output.append("### " + text + "\n")
                    continue

                # Question / assessment sections
                if any(k in text.lower() for k in QUESTION_KW):
                    output.append("## " + text + "\n")
                    continue

                # Special conceptual sections
                if any(k in text.lower() for k in SPECIAL_KW):
                    output.append("## " + text + "\n")
                    continue

                # Default downgrade
                output.append("## " + text + "\n")
                continue

            # ---------------- OUTSIDE CHAPTER ----------------
            output.append(stripped + "\n")
            continue

        # ---------------- NORMAL TEXT ----------------
        output.append(line)

    return output
import os

def process_subject_folder(subject_path, overwrite=True):
    md_path = os.path.join(subject_path, "full.md")

    if not os.path.exists(md_path):
        print(f"⚠️ Skipping (no full.md): {subject_path}")
        return

    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    cleaned = normalize_markdown(lines)

    output_path = md_path if overwrite else md_path.replace(".md", "_cleaned.md")

    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(cleaned)

    print(f"✔ Processed: {output_path}")

def process_textbook_root(root_dir, overwrite=True):
    for entry in os.listdir(root_dir):
        subject_path = os.path.join(root_dir, entry)

        if os.path.isdir(subject_path):
            process_subject_folder(subject_path, overwrite)

def main():
    root_folder = "DataBase"  # change if needed
    overwrite_existing = False      # False → creates content_cleaned.md
    process_textbook_root(root_folder, overwrite_existing)

if __name__ == "__main__":
    main()
