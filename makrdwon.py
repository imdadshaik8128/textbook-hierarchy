import os
import glob
from markitdown import MarkItDown

def convert_pdfs_to_markdown(input_dir="input_pdfs", output_dir="markdown_output"):
    """
    Convert all PDF files in input_dir to Markdown files in output_dir
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize MarkItDown
    md = MarkItDown(enable_plugins=False)
    
    # Find all PDF files
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in the current directory.")
        return
    
    print(f"Found {len(pdf_files)} PDF files to convert...")
    
    for pdf_file in pdf_files:
        try:
            # Get base filename without extension
            base_name = os.path.splitext(os.path.basename(pdf_file))[0]
            output_file = os.path.join(output_dir, f"{base_name}.md")
            
            print(f"Converting: {pdf_file} -> {output_file}")
            
            # Convert the PDF
            result = md.convert(pdf_file)
            
            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result.text_content)
            
            print(f"✓ Successfully converted {pdf_file}")
            
        except Exception as e:
            print(f"✗ Error converting {pdf_file}: {str(e)}")
    
    print(f"\nConversion complete! Check the {output_dir} directory.")

if __name__ == "__main__":
    convert_pdfs_to_markdown() 