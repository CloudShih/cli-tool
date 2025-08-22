#!/usr/bin/env python3
"""
Test QPDF password parameter format
"""

import sys
import subprocess
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_qpdf_password_format():
    """Test different QPDF password parameter formats"""
    print("Testing QPDF password parameter formats...")
    
    # Test the format QPDF expects
    test_commands = [
        # Test 1: Old format (should fail)
        ["qpdf", "--password", "test", "--check", "nonexistent.pdf"],
        
        # Test 2: New format (should work for syntax, but file doesn't exist)
        ["qpdf", "--password=test", "--check", "nonexistent.pdf"],
        
        # Test 3: Help to see correct syntax
        ["qpdf", "--help=--password"]
    ]
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"\nTest {i}: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            print(f"Return code: {result.returncode}")
            print(f"Stdout: {result.stdout[:200]}...")
            print(f"Stderr: {result.stderr[:200]}...")
        except subprocess.TimeoutExpired:
            print("Command timed out")
        except Exception as e:
            print(f"Error: {e}")

def test_our_command_builder():
    """Test our command builder with the fix"""
    try:
        from tools.qpdf.core.data_models import QPDFOperation, QPDFOperationType, build_qpdf_command
        
        # Create a test operation
        operation = QPDFOperation(
            operation_type=QPDFOperationType.DECRYPT,
            input_file="test.pdf",
            output_file="output.pdf",
            password="testpass"
        )
        
        cmd = build_qpdf_command(operation)
        print(f"\nOur command builder generates: {cmd}")
        
        # Check if password format is correct
        password_found = False
        for arg in cmd:
            if arg.startswith("--password="):
                password_found = True
                print(f"✓ Password format looks correct: {arg}")
                break
        
        if not password_found:
            print("✗ Password format not found in command")
        
        return cmd
        
    except Exception as e:
        print(f"Command builder test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_qpdf_password_format()
    test_our_command_builder()