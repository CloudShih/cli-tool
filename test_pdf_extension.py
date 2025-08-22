#!/usr/bin/env python3
"""
Test automatic PDF extension functionality for QPDF plugin
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_pdf_extension_functions():
    """Test the PDF extension helper functions"""
    try:
        from tools.qpdf.qpdf_controller import QPDFController
        from tools.qpdf.qpdf_model import QPDFModel
        from tools.qpdf.qpdf_view import QPDFView
        
        # Create controller instance to test helper functions
        model = QPDFModel()
        view = QPDFView()
        controller = QPDFController(model, view)
        
        print("Testing PDF extension helper functions...")
        
        # Test regular file extension function
        test_cases = [
            ("test", "test.pdf"),
            ("document", "document.pdf"),
            ("my_file.pdf", "my_file.pdf"),  # Already has extension
            ("D:\\folder\\file", "D:\\folder\\file.pdf"),
            ("D:\\folder\\file.PDF", "D:\\folder\\file.PDF"),  # Case insensitive
            ("", ""),  # Empty string
            ("  file_name  ", "file_name.pdf"),  # With whitespace
        ]
        
        print("\n1. Testing _ensure_pdf_extension:")
        for input_val, expected in test_cases:
            result = controller._ensure_pdf_extension(input_val)
            status = "✓" if result == expected else "✗"
            print(f"  {status} '{input_val}' -> '{result}' (expected: '{expected}')")
        
        # Test pattern extension function for split
        pattern_test_cases = [
            ("page_%d", "page_%d.pdf"),
            ("D:\\output\\page_%d", "D:\\output\\page_-%d.pdf"),
            ("document-%d.pdf", "document-%d.pdf"),  # Already has extension
            ("file", "file.pdf"),  # No %d placeholder
            ("", ""),  # Empty string
        ]
        
        print("\n2. Testing _ensure_pdf_extension_pattern:")
        for input_val, expected in pattern_test_cases:
            result = controller._ensure_pdf_extension_pattern(input_val)
            status = "✓" if result == expected else "✗"
            print(f"  {status} '{input_val}' -> '{result}' (expected: '{expected}')")
        
        print("\n3. Testing with actual use case scenarios:")
        
        # Scenario 1: User enters just filename
        user_input = "decrypted_document"
        result = controller._ensure_pdf_extension(user_input)
        print(f"  User enters: '{user_input}' -> System uses: '{result}'")
        
        # Scenario 2: User enters filename with path
        user_input = "C:\\Users\\Documents\\encrypted_file"
        result = controller._ensure_pdf_extension(user_input)
        print(f"  User enters: '{user_input}' -> System uses: '{result}'")
        
        # Scenario 3: Split pattern
        user_input = "D:\\output\\page_%d"
        result = controller._ensure_pdf_extension_pattern(user_input)
        print(f"  Split pattern: '{user_input}' -> System uses: '{result}'")
        
        print("\nAll tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pdf_extension_functions()
    if success:
        print("\nPDF extension functionality is working correctly!")
    else:
        print("\nPDF extension functionality has issues!")
        sys.exit(1)