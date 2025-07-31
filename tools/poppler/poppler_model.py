import subprocess
import os
import tempfile
import shutil
import logging
from ansi2html import Ansi2HTMLConverter
from config.config_manager import config_manager

logger = logging.getLogger(__name__)

class PopplerModel:
    def __init__(self):
        # 從配置管理器獲取 poppler 工具路徑
        poppler_config = config_manager.get_tool_config('poppler')
        self.pdfinfo_path = poppler_config.get('pdfinfo_path', 'pdfinfo')
        self.pdftotext_path = poppler_config.get('pdftotext_path', 'pdftotext')
        self.pdfimages_path = poppler_config.get('pdfimages_path', 'pdfimages')
        self.pdfseparate_path = poppler_config.get('pdfseparate_path', 'pdfseparate')
        self.pdfunite_path = poppler_config.get('pdfunite_path', 'pdfunite')
        self.pdftoppm_path = poppler_config.get('pdftoppm_path', 'pdftoppm')
        self.pdftohtml_path = poppler_config.get('pdftohtml_path', 'pdftohtml')
        self.qpdf_path = poppler_config.get('qpdf_path', 'qpdf')
        
        logger.info("PopplerModel initialized with configuration")

    def _execute_command(self, command):
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                shell=False
            )
            stdout, stderr = process.communicate()

            # Filter out known pdfminer.six warnings
            filtered_stderr_lines = []
            for line in stderr.splitlines():
                if "Cannot set gray non-stroke color because /'P" not in line:
                    filtered_stderr_lines.append(line)
            stderr = "\n".join(filtered_stderr_lines)

            conv = Ansi2HTMLConverter()
            html_output = conv.convert(stdout, full=False)
            html_error = conv.convert(stderr, full=False)
            
            return html_output, html_error

        except FileNotFoundError:
            return "", f"Error: Command '{command[0]}' not found. Please ensure Poppler/QPDF utilities are installed and in your system's PATH."
        except UnicodeDecodeError as e:
            return "", f"UnicodeDecodeError: {e}. The command output could not be decoded. This might indicate an issue with the external tool's output encoding."
        except Exception as e:
            return "", f"An unexpected error occurred: {e}"

    def get_pdf_info(self, pdf_path):
        command = [self.pdfinfo_path, pdf_path]
        return self._execute_command(command)

    def convert_pdf_to_text(self, pdf_path, output_txt_path):
        command = [self.pdftotext_path, pdf_path, output_txt_path]
        return self._execute_command(command)

    def extract_pdf_images(self, pdf_path, output_directory, file_prefix, image_format):
        import os
        if output_directory and not os.path.exists(output_directory):
            os.makedirs(output_directory)
        
        output_path = os.path.join(output_directory, file_prefix)
        
        command = [self.pdfimages_path, pdf_path, output_path]
        
        # Add format specific options
        if image_format == "png":
            command.insert(1, "-png")

        return self._execute_command(command)

    def separate_pdf_pages(self, pdf_path, output_prefix):
        command = [self.pdfseparate_path, pdf_path, output_prefix]
        return self._execute_command(command)

    def unite_pdfs(self, input_paths, output_path):
        command = [self.pdfunite_path] + input_paths + [output_path]
        return self._execute_command(command)

    def decrypt_pdf(self, input_path, output_path):
        command = [self.qpdf_path, "--decrypt", input_path, output_path]
        return self._execute_command(command)

    def convert_pdf_to_html(self, pdf_path, output_html_path):
        command = [self.pdftohtml_path, '-s', '-c', '-noframes', pdf_path, output_html_path]
        return self._execute_command(command)

    

    def convert_pdf_to_ppm(self, pdf_path, output_prefix, image_format, start_page=None, end_page=None):
        command = [self.pdftoppm_path]

        if image_format == "png":
            command.append("-png")
        elif image_format == "jpeg":
            command.append("-jpeg")
        # PPM is default, no specific flag needed

        if start_page:
            command.extend(["-f", str(start_page)])
        if end_page:
            command.extend(["-l", str(end_page)])

        command.extend([pdf_path, output_prefix])
        return self._execute_command(command)

    