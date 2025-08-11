import os
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
import math

def split_pdf_by_size(input_path, max_size_mb=2, output_dir=None):
    """
    Split a PDF into smaller chunks based on file size
    
    Args:
        input_path: Path to the input PDF file
        max_size_mb: Maximum size per chunk in MB (default: 2MB for optimal speed)
        output_dir: Directory to save chunks (default: same as input file)
    
    Returns:
        List of paths to the created PDF chunks
    """
    # Get input file info
    input_size_mb = os.path.getsize(input_path) / (1024 * 1024)
    filename = os.path.basename(input_path)
    name_without_ext = os.path.splitext(filename)[0]
    
    if output_dir is None:
        output_dir = os.path.dirname(input_path)
    
    # Create output directory if it doesn't exist
    chunks_dir = os.path.join(output_dir, f"{name_without_ext}_chunks")
    if not os.path.exists(chunks_dir):
        os.makedirs(chunks_dir)
    
    print(f"Original PDF size: {input_size_mb:.2f} MB")
    print(f"Target chunk size: {max_size_mb} MB")
    
    # If file is already small enough, just copy it
    if input_size_mb <= max_size_mb:
        print("PDF is already small enough, no splitting needed")
        chunk_path = os.path.join(chunks_dir, f"{name_without_ext}_chunk_001.pdf")
        import shutil
        shutil.copy2(input_path, chunk_path)
        return [chunk_path]
    
    # Read the PDF
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    
    # Estimate pages per chunk with maximum limit
    estimated_chunks = math.ceil(input_size_mb / max_size_mb)
    pages_per_chunk = max(1, total_pages // estimated_chunks)
    
    # Enforce maximum of 35 pages per chunk
    if pages_per_chunk > 35:
        pages_per_chunk = 35
        # Recalculate chunks based on page limit
        estimated_chunks = math.ceil(total_pages / pages_per_chunk)
    
    print(f"Total pages: {total_pages}")
    print(f"Estimated chunks: {estimated_chunks}")
    print(f"Pages per chunk: {pages_per_chunk}")
    
    chunk_paths = []
    chunk_num = 1
    
    for start_page in range(0, total_pages, pages_per_chunk):
        end_page = min(start_page + pages_per_chunk, total_pages)
        
        # Create a new PDF writer for this chunk
        writer = PdfWriter()
        
        # Add pages to this chunk
        for page_num in range(start_page, end_page):
            writer.add_page(reader.pages[page_num])
        
        # Save the chunk
        chunk_filename = f"{name_without_ext}_chunk_{chunk_num:03d}.pdf"
        chunk_path = os.path.join(chunks_dir, chunk_filename)
        
        with open(chunk_path, 'wb') as output_file:
            writer.write(output_file)
        
        chunk_size_mb = os.path.getsize(chunk_path) / (1024 * 1024)
        print(f"Created chunk {chunk_num}: {chunk_filename} ({chunk_size_mb:.2f} MB, pages {start_page+1}-{end_page})")
        
        chunk_paths.append(chunk_path)
        chunk_num += 1
    
    print(f"\nPDF split into {len(chunk_paths)} chunks")
    print(f"Chunks saved in: {chunks_dir}")
    
    return chunk_paths

def split_pdf_by_pages(input_path, pages_per_chunk=35, output_dir=None):
    """
    Split a PDF into smaller chunks based on number of pages
    
    Args:
        input_path: Path to the input PDF file
        pages_per_chunk: Number of pages per chunk (default: 35, max recommended)
        output_dir: Directory to save chunks (default: same as input file)
    
    Returns:
        List of paths to the created PDF chunks
    """
    # Get input file info
    filename = os.path.basename(input_path)
    name_without_ext = os.path.splitext(filename)[0]
    
    if output_dir is None:
        output_dir = os.path.dirname(input_path)
    
    # Create output directory if it doesn't exist
    chunks_dir = os.path.join(output_dir, f"{name_without_ext}_chunks")
    if not os.path.exists(chunks_dir):
        os.makedirs(chunks_dir)
    
    # Read the PDF
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    
    print(f"Total pages: {total_pages}")
    print(f"Pages per chunk: {pages_per_chunk}")
    
    chunk_paths = []
    chunk_num = 1
    
    for start_page in range(0, total_pages, pages_per_chunk):
        end_page = min(start_page + pages_per_chunk, total_pages)
        
        # Create a new PDF writer for this chunk
        writer = PdfWriter()
        
        # Add pages to this chunk
        for page_num in range(start_page, end_page):
            writer.add_page(reader.pages[page_num])
        
        # Save the chunk
        chunk_filename = f"{name_without_ext}_chunk_{chunk_num:03d}.pdf"
        chunk_path = os.path.join(chunks_dir, chunk_filename)
        
        with open(chunk_path, 'wb') as output_file:
            writer.write(output_file)
        
        chunk_size_mb = os.path.getsize(chunk_path) / (1024 * 1024)
        print(f"Created chunk {chunk_num}: {chunk_filename} ({chunk_size_mb:.2f} MB, pages {start_page+1}-{end_page})")
        
        chunk_paths.append(chunk_path)
        chunk_num += 1
    
    print(f"\nPDF split into {len(chunk_paths)} chunks")
    print(f"Chunks saved in: {chunks_dir}")
    
    return chunk_paths

# Example usage:
# For size-based splitting (recommended for OCR website limits)
# chunk_paths = split_pdf_by_size("/path/to/large_file.pdf", max_size_mb=5)

# For page-based splitting
# chunk_paths = split_pdf_by_pages("/path/to/large_file.pdf", pages_per_chunk=10)

print("PDF splitting functions ready!")