import pytest
import os
from unittest.mock import patch
from cli_tool.pdf_decryptor import decrypt_pdf
import pikepdf

# Helper function to create a dummy PDF for testing
def create_dummy_pdf(path, password=None):
    pdf = pikepdf.new()
    if password:
        pdf.save(path, encryption=pikepdf.Encryption(owner=password, user=password, R=4))
    else:
        pdf.save(path)

@pytest.fixture
def setup_pdf_files(tmp_path):
    # Unprotected PDF
    unprotected_pdf_path = tmp_path / "unprotected.pdf"
    create_dummy_pdf(unprotected_pdf_path)

    # Password-protected PDF
    protected_pdf_path = tmp_path / "protected.pdf"
    correct_password = "test_password"
    create_dummy_pdf(protected_pdf_path, password=correct_password)

    # Output path for decryption
    output_pdf_path = tmp_path / "decrypted.pdf"

    return {
        "unprotected_pdf_path": str(unprotected_pdf_path),
        "protected_pdf_path": str(protected_pdf_path),
        "correct_password": correct_password,
        "output_pdf_path": str(output_pdf_path),
    }

def test_decrypt_pdf_unprotected(setup_pdf_files):
    paths = setup_pdf_files
    result = decrypt_pdf(paths["unprotected_pdf_path"], paths["output_pdf_path"])
    assert result is True
    assert os.path.exists(paths["output_pdf_path"])

def test_decrypt_pdf_with_correct_password(setup_pdf_files):
    paths = setup_pdf_files
    result = decrypt_pdf(paths["protected_pdf_path"], paths["output_pdf_path"], paths["correct_password"])
    assert result is True
    assert os.path.exists(paths["output_pdf_path"])

def test_decrypt_pdf_with_incorrect_password(setup_pdf_files):
    paths = setup_pdf_files
    incorrect_password = "wrong_password"
    result = decrypt_pdf(paths["protected_pdf_path"], paths["output_pdf_path"], incorrect_password)
    assert result is False
    assert not os.path.exists(paths["output_pdf_path"])

def test_decrypt_pdf_non_existent_file(setup_pdf_files):
    paths = setup_pdf_files
    non_existent_path = paths["tmp_path"] / "non_existent.pdf"
    result = decrypt_pdf(str(non_existent_path), paths["output_pdf_path"])
    assert result is False
    assert not os.path.exists(paths["output_pdf_path"])

def test_decrypt_pdf_invalid_pdf_format(setup_pdf_files):
    paths = setup_pdf_files
    invalid_pdf_path = paths["tmp_path"] / "invalid.pdf"
    with open(invalid_pdf_path, "w") as f:
        f.write("This is not a PDF content")
    result = decrypt_pdf(str(invalid_pdf_path), paths["output_pdf_path"])
    assert result is False
    assert not os.path.exists(paths["output_pdf_path"])
