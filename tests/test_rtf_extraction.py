import os
import tempfile
import sys
from pathlib import Path

# Add the project root to the path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

from backend.legal_ai.document_ingest import extract_text_from_rtf

def test_extract_text_from_rtf():
    """Test the RTF text extraction function"""
    
    # Create a simple RTF test file
    test_rtf_content = r"""{\rtf1\ansi\deff0 {\fonttbl {\f0 Times New Roman;}}
\f0\fs24 This is a test RTF document.
\par
\par
It contains multiple paragraphs and formatting.
\par
\par
This should be extracted as plain text.}"""
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.rtf', delete=False, encoding='utf-8') as f:
        f.write(test_rtf_content)
        temp_file_path = f.name
    
    try:
        # Test the extraction
        extracted_text = extract_text_from_rtf(temp_file_path)
        
        # Print results
        print("=== RTF Extraction Test ===")
        print(f"Original RTF content length: {len(test_rtf_content)} characters")
        print(f"Extracted text length: {len(extracted_text)} characters")
        print(f"Extracted text preview: {extracted_text[:200]}...")
        
        # Basic assertions
        assert len(extracted_text) > 0, "Extracted text should not be empty"
        assert "test RTF document" in extracted_text, "Should contain expected text"
        assert "multiple paragraphs" in extracted_text, "Should contain expected text"
        
        print("✅ RTF extraction test passed!")
        
        return True
        
    except Exception as e:
        print(f"❌ RTF extraction test failed: {e}")
        return False
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

def test_real_rtf_files():
    """Test extraction on actual RTF files in the data directory"""
    
    data_dir = Path("./data")
    rtf_files = list(data_dir.glob("*.rtf"))
    
    if not rtf_files:
        print("No RTF files found in data directory")
        print(f"Looking in: {data_dir.absolute()}")
        return
    
    print(f"\n=== Testing {len(rtf_files)} real RTF files ===")
    
    for rtf_file in rtf_files:
        try:
            print(f"\nProcessing: {rtf_file.name}")
            extracted_text = extract_text_from_rtf(rtf_file)
            
            print(f"  File size: {rtf_file.stat().st_size / (1024*1024):.1f} MB")
            print(f"  Extracted text length: {len(extracted_text)} characters")
            print(f"  Preview: {extracted_text[:100]}...")
            
            # Basic validation
            assert len(extracted_text) > 1000, f"Extracted text too short for {rtf_file.name}"
            
            print(f"  ✅ Successfully processed {rtf_file.name}")
            
        except Exception as e:
            print(f"  ❌ Failed to process {rtf_file.name}: {e}")

if __name__ == "__main__":
    # Run synthetic test
    test_extract_text_from_rtf()
    
    # Run real file tests
    test_real_rtf_files() 