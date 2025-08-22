#!/usr/bin/env python3
"""
Test QPDF command generation with correct parameter formats
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_qpdf_command_formats():
    """Test various QPDF command formats"""
    try:
        from tools.qpdf.core.data_models import (
            QPDFOperation, QPDFOperationType, EncryptionLevel, CompressionLevel,
            build_qpdf_command
        )
        
        print("Testing QPDF command generation...")
        
        # Test 1: Decrypt with password
        print("\n1. Testing DECRYPT with password:")
        decrypt_op = QPDFOperation(
            operation_type=QPDFOperationType.DECRYPT,
            input_file="encrypted.pdf",
            output_file="decrypted.pdf",
            password="secret123"
        )
        decrypt_cmd = build_qpdf_command(decrypt_op)
        print(f"Command: {' '.join(decrypt_cmd)}")
        
        # Check password format
        password_correct = any(arg.startswith("--password=") for arg in decrypt_cmd)
        print(f"Password format correct: {password_correct}")
        
        # Test 2: Encrypt
        print("\n2. Testing ENCRYPT:")
        encrypt_op = QPDFOperation(
            operation_type=QPDFOperationType.ENCRYPT,
            input_file="plain.pdf",
            output_file="encrypted.pdf",
            user_password="user123",
            owner_password="owner123",
            encryption_level=EncryptionLevel.AES_256
        )
        encrypt_cmd = build_qpdf_command(encrypt_op)
        print(f"Command: {' '.join(encrypt_cmd)}")
        
        # Test 3: JSON info with keys
        print("\n3. Testing JSON_INFO with keys:")
        json_op = QPDFOperation(
            operation_type=QPDFOperationType.JSON_INFO,
            input_file="test.pdf",
            json_keys=["pages", "objects"]
        )
        json_cmd = build_qpdf_command(json_op)
        print(f"Command: {' '.join(json_cmd)}")
        
        # Check json-key format
        json_key_correct = any(arg.startswith("--json-key=") for arg in json_cmd)
        print(f"JSON key format correct: {json_key_correct}")
        
        # Test 4: Rotate pages
        print("\n4. Testing ROTATE:")
        rotate_op = QPDFOperation(
            operation_type=QPDFOperationType.ROTATE,
            input_file="test.pdf",
            output_file="rotated.pdf",
            rotation_angle=90,
            rotation_pages="1-5"
        )
        rotate_cmd = build_qpdf_command(rotate_op)
        print(f"Command: {' '.join(rotate_cmd)}")
        
        # Check rotate format
        rotate_correct = any(arg.startswith("--rotate=") for arg in rotate_cmd)
        print(f"Rotate format correct: {rotate_correct}")
        
        # Test 5: Compression
        print("\n5. Testing compression options:")
        compress_op = QPDFOperation(
            operation_type=QPDFOperationType.LINEARIZE,
            input_file="test.pdf",
            output_file="compressed.pdf",
            compression_level=CompressionLevel.HIGH,
            normalize_content=True
        )
        compress_cmd = build_qpdf_command(compress_op)
        print(f"Command: {' '.join(compress_cmd)}")
        
        # Check compression format
        compress_correct = any("--compress-streams=y" in arg for arg in compress_cmd)
        normalize_correct = any("--normalize-content=y" in arg for arg in compress_cmd)
        print(f"Compression format correct: {compress_correct}")
        print(f"Normalize format correct: {normalize_correct}")
        
        print("\n=== Summary ===")
        all_correct = all([
            password_correct,
            json_key_correct, 
            rotate_correct,
            compress_correct,
            normalize_correct
        ])
        
        if all_correct:
            print("All parameter formats are correct!")
            return True
        else:
            print("Some parameter formats need fixing!")
            return False
            
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_qpdf_command_formats()
    if success:
        print("\nQPDF command format tests passed!")
    else:
        print("\nQPDF command format tests failed!")
        sys.exit(1)