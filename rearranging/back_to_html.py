import re

# ---------- CONFIG ----------
file1 = "file1.md"   # HTML tables
file2 = "file2.md"   # Markdown tables
output_file = "final_output.md"
# ----------------------------

def extract_html_tables(content):
    pattern = r"<table.*?>.*?</table>"
    return re.findall(pattern, content, flags=re.DOTALL)

def replace_markdown_tables(md_content, html_tables):
    # Markdown table pattern
    md_table_pattern = r"(?:\|.*\n)+"
    
    table_index = 0

    def replacer(match):
        nonlocal table_index
        if table_index < len(html_tables):
            table = html_tables[table_index]
            table_index += 1
            return "\n" + table + "\n"
        return match.group(0)

    return re.sub(md_table_pattern, replacer, md_content)

# Read files
with open(file1, "r", encoding="utf-8") as f:
    html_content = f.read()

with open(file2, "r", encoding="utf-8") as f:
    md_content = f.read()

# Extract HTML tables
html_tables = extract_html_tables(html_content)

# Replace markdown tables
new_content = replace_markdown_tables(md_content, html_tables)

# Save result
with open(output_file, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Done! Output saved as", output_file)
