import subprocess
from ansi2html import Ansi2HTMLConverter
from config.config_manager import config_manager
import logging

logger = logging.getLogger(__name__)

class FdModel:
    def __init__(self):
        # 從配置管理器獲取 fd 執行檔路徑
        self.fd_executable_path = config_manager.get('tools.fd.executable_path')
        logger.info(f"FdModel initialized with executable path: {self.fd_executable_path}")

    def execute_fd_command(self, pattern, path, extension, search_type_index, hidden, case_sensitive):
        command = [self.fd_executable_path]
        
        if pattern:
            command.append(pattern)
        
        if path:
            command.append(path)
        
        if extension:
            command.extend(["-e", extension])

        if search_type_index == 1: # Files only
            command.extend(["-t", "f"])
        elif search_type_index == 2: # Directories only
            command.extend(["-t", "d"])

        if hidden:
            command.append("--hidden")
        if case_sensitive:
            command.append("--case-sensitive")

        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False,
                shell=False
            )
            stdout_bytes, stderr_bytes = process.communicate()

            stdout = stdout_bytes.decode('utf-8', errors='ignore')
            stderr = stderr_bytes.decode('utf-8', errors='ignore')

            conv = Ansi2HTMLConverter()
            
            html_output = ""
            html_error = ""

            if stdout:
                html_output = conv.convert(stdout, full=False)
            if stderr:
                html_error = conv.convert(stderr, full=False)
            
            return html_output, html_error

        except FileNotFoundError:
            return "", "Error: 'fd' executable not found at the specified path. Please verify the path."
        except Exception as e:
            return "", f"An unexpected error occurred: {e}"

