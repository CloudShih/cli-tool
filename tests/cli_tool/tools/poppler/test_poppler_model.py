import pytest
from unittest.mock import MagicMock, patch
import os
import subprocess
from cli_tool.tools.poppler.poppler_model import PopplerModel
from ansi2html import Ansi2HTMLConverter

# Mock the PopplerModel to prevent actual external command execution
@pytest.fixture
def poppler_model():
    return PopplerModel()

@pytest.fixture
def ansi2html_converter():
    return Ansi2HTMLConverter()

@patch('subprocess.Popen')
def test_decrypt_pdf_success(mock_popen, poppler_model, ansi2html_converter):
    mock_popen.return_value.communicate.return_value = ('PDF decrypted successfully', '')
    mock_popen.return_value.returncode = 0
    input_path = r"D:\geminiCLI\MT6631 Design Notice V1.2_20200622.pdf"
    output_path = r"D:\geminiCLI\MT6631 Design Notice V1.2_20200622_decrypted.pdf"
    result = poppler_model.decrypt_pdf(input_path, output_path)
    expected_stdout_html = ansi2html_converter.convert('PDF decrypted successfully', full=False)
    expected_stderr_html = ansi2html_converter.convert('', full=False)
    assert result == (expected_stdout_html, expected_stderr_html)
    mock_popen.assert_called_once_with(
        ['qpdf', '--decrypt', input_path, output_path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', shell=False
    )

@patch('subprocess.Popen')
def test_decrypt_pdf_failure(mock_popen, poppler_model, ansi2html_converter):
    mock_popen.return_value.communicate.return_value = ('', 'Error decrypting PDF')
    mock_popen.return_value.returncode = 1
    input_path = r"D:\geminiCLI\MT6631 Design Notice V1.2_20200622.pdf"
    output_path = r"D:\geminiCLI\MT6631 Design Notice V1.2_20200622_decrypted.pdf"
    result = poppler_model.decrypt_pdf(input_path, output_path)
    expected_stdout_html = ansi2html_converter.convert('', full=False)
    expected_stderr_html = ansi2html_converter.convert('Error decrypting PDF', full=False)
    assert result == (expected_stdout_html, expected_stderr_html)

@patch('subprocess.Popen')
def test_convert_pdf_to_html_success(mock_popen, poppler_model, ansi2html_converter):
    mock_popen.return_value.communicate.return_value = ('PDF converted to HTML successfully', '')
    mock_popen.return_value.returncode = 0
    input_path = r"D:\geminiCLI\products\PN7160_PN7161 Near Field Communication (NFC) controller.pdf"
    output_path = r"D:\geminiCLI\products\PN7160.html"
    result = poppler_model.convert_pdf_to_html(input_path, output_path)
    expected_stdout_html = ansi2html_converter.convert('PDF converted to HTML successfully', full=False)
    expected_stderr_html = ansi2html_converter.convert('', full=False)
    assert result == (expected_stdout_html, expected_stderr_html)
    mock_popen.assert_called_once_with(
        ['pdftohtml', '-s', '-c', '-noframes', input_path, output_path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', shell=False
    )

@patch('subprocess.Popen')
def test_convert_pdf_to_html_failure(mock_popen, poppler_model, ansi2html_converter):
    mock_popen.return_value.communicate.return_value = ('', 'Error converting PDF to HTML')
    mock_popen.return_value.returncode = 1
    input_path = r"D:\geminiCLI\products\PN7160_PN7161 Near Field Communication (NFC) controller.pdf"
    output_path = r"D:\geminiCLI\products\PN7160.html"
    result = poppler_model.convert_pdf_to_html(input_path, output_path)
    expected_stdout_html = ansi2html_converter.convert('', full=False)
    expected_stderr_html = ansi2html_converter.convert('Error converting PDF to HTML', full=False)
    assert result == (expected_stdout_html, expected_stderr_html)

@patch('subprocess.Popen')
def test_convert_pdf_to_text_success(mock_popen, poppler_model, ansi2html_converter):
    mock_popen.return_value.communicate.return_value = ('PDF converted to text successfully', '')
    mock_popen.return_value.returncode = 0
    input_path = r"D:\geminiCLI\products\PN7160_PN7161 Near Field Communication (NFC) controller.pdf"
    output_path = r"D:\geminiCLI\products\PN7160.txt"
    result = poppler_model.convert_pdf_to_text(input_path, output_path)
    expected_stdout_html = ansi2html_converter.convert('PDF converted to text successfully', full=False)
    expected_stderr_html = ansi2html_converter.convert('', full=False)
    assert result == (expected_stdout_html, expected_stderr_html)
    mock_popen.assert_called_once_with(
        ['pdftotext', input_path, output_path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', shell=False
    )

@patch('subprocess.Popen')
def test_convert_pdf_to_text_failure(mock_popen, poppler_model, ansi2html_converter):
    mock_popen.return_value.communicate.return_value = ('', 'Error converting PDF to text')
    mock_popen.return_value.returncode = 1
    input_path = r"D:\geminiCLI\products\PN7160_PN7161 Near Field Communication (NFC) controller.pdf"
    output_path = r"D:\geminiCLI\products\PN7160.txt"
    result = poppler_model.convert_pdf_to_text(input_path, output_path)
    expected_stdout_html = ansi2html_converter.convert('', full=False)
    expected_stderr_html = ansi2html_converter.convert('Error converting PDF to text', full=False)
    assert result == (expected_stdout_html, expected_stderr_html)

@patch('subprocess.Popen')
def test_extract_pdf_images_success(mock_popen, poppler_model, ansi2html_converter):
    mock_popen.return_value.communicate.return_value = ('PDF images extracted successfully', '')
    mock_popen.return_value.returncode = 0
    input_path = r"D:\geminiCLI\products\PN7160_PN7161 Near Field Communication (NFC) controller.pdf"
    output_directory = r"D:\geminiCLI\products"
    file_prefix = "PN7160_image"
    image_format = "png"
    result = poppler_model.extract_pdf_images(input_path, output_directory, file_prefix, image_format)
    expected_stdout_html = ansi2html_converter.convert('PDF images extracted successfully', full=False)
    expected_stderr_html = ansi2html_converter.convert('', full=False)
    assert result == (expected_stdout_html, expected_stderr_html)
    mock_popen.assert_called_once_with(
        ['pdfimages', '-png', input_path, os.path.join(output_directory, file_prefix)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', shell=False
    )

@patch('subprocess.Popen')
def test_extract_pdf_images_failure(mock_popen, poppler_model, ansi2html_converter):
    mock_popen.return_value.communicate.return_value = ('', 'Error extracting PDF images')
    mock_popen.return_value.returncode = 1
    input_path = r"D:\geminiCLI\products\PN7160_PN7161 Near Field Communication (NFC) controller.pdf"
    output_directory = r"D:\geminiCLI\products"
    file_prefix = "PN7160_image"
    image_format = "png"
    result = poppler_model.extract_pdf_images(input_path, output_directory, file_prefix, image_format)
    expected_stdout_html = ansi2html_converter.convert('', full=False)
    expected_stderr_html = ansi2html_converter.convert('Error extracting PDF images', full=False)
    assert result == (expected_stdout_html, expected_stderr_html)

@patch('subprocess.Popen')
def test_get_pdf_info_success(mock_popen, poppler_model, ansi2html_converter):
    mock_popen.return_value.communicate.return_value = ('Title: Test PDF\nPages: 10', '')
    mock_popen.return_value.returncode = 0
    input_path = r"D:\geminiCLI\products\PN7160_PN7161 Near Field Communication (NFC) controller.pdf"
    result = poppler_model.get_pdf_info(input_path)
    expected_stdout_html = ansi2html_converter.convert('Title: Test PDF\nPages: 10', full=False)
    expected_stderr_html = ansi2html_converter.convert('', full=False)
    assert result == (expected_stdout_html, expected_stderr_html)
    mock_popen.assert_called_once_with(
        ['pdfinfo', input_path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', shell=False
    )

@patch('subprocess.Popen')
def test_get_pdf_info_failure(mock_popen, poppler_model, ansi2html_converter):
    mock_popen.return_value.communicate.return_value = ('', 'Error getting PDF info')
    mock_popen.return_value.returncode = 1
    input_path = r"D:\geminiCLI\products\PN7160_PN7161 Near Field Communication (NFC) controller.pdf"
    result = poppler_model.get_pdf_info(input_path)
    expected_stdout_html = ansi2html_converter.convert('', full=False)
    expected_stderr_html = ansi2html_converter.convert('Error getting PDF info', full=False)
    assert result == (expected_stdout_html, expected_stderr_html)
