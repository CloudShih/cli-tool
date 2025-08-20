import logging
from typing import Any, Dict, Protocol

from .dust_model import DustModel
from .dust_view_redesigned import DustViewRedesigned
from .dust_controller import DustController


logger = logging.getLogger(__name__)


class IDustAnalyzer(Protocol):
    """Interface for dust analysis services."""

    def get_configuration_schema(self) -> Dict[str, Any]:
        ...

    def get_settings(self) -> Dict[str, Any]:
        ...

    def apply_settings(self, settings: Dict[str, Any]) -> None:
        ...

    def handle_directory_analysis(self, directory_path: str) -> bool:
        ...

    def get_status_info(self) -> Dict[str, Any]:
        ...

    def execute_command(self, command: str, args: Dict[str, Any] | None = None) -> Any:
        ...

    def check_tools_availability(self) -> bool:
        ...


class DustService(IDustAnalyzer):
    """Service layer handling dust settings and command execution."""

    def __init__(self, model: DustModel, view: DustViewRedesigned, controller: DustController):
        self._model = model
        self._view = view
        self._controller = controller

    # --- Configuration ---
    def get_configuration_schema(self) -> Dict[str, Any]:
        return {
            "executable_path": {
                "type": "string",
                "default": "dust",
                "description": "dust 執行檔路徑",
            },
            "default_depth": {
                "type": "integer",
                "default": 3,
                "minimum": 1,
                "maximum": 10,
                "description": "預設掃描深度",
            },
            "default_limit": {
                "type": "integer",
                "default": 30,
                "minimum": 5,
                "maximum": 1000,
                "description": "預設顯示項目數量限制",
            },
            "show_full_paths": {
                "type": "boolean",
                "default": False,
                "description": "顯示完整路徑",
            },
            "files_only": {
                "type": "boolean",
                "default": False,
                "description": "只顯示檔案（不含目錄）",
            },
            "apparent_size": {
                "type": "boolean",
                "default": True,
                "description": "使用檔案實際大小而非磁碟佔用空間",
            },
            "output_format": {
                "type": "string",
                "default": "terminal",
                "enum": ["terminal", "json", "csv"],
                "description": "輸出格式",
            },
            "color_scheme": {
                "type": "string",
                "default": "auto",
                "enum": ["auto", "always", "never"],
                "description": "顏色方案",
            },
            "use_cache": {
                "type": "boolean",
                "default": True,
                "description": "是否使用快取功能",
            },
            "cache_ttl": {
                "type": "integer",
                "default": 1800,
                "minimum": 300,
                "maximum": 86400,
                "description": "快取存留時間（秒）",
            },
            "recent_directories": {
                "type": "array",
                "default": [],
                "description": "最近分析的目錄列表",
            },
        }

    def get_settings(self) -> Dict[str, Any]:
        try:
            return {
                "max_depth": self._view.dust_max_depth_input.value() if self._view else 3,
                "number_of_lines": self._view.dust_lines_input.value() if self._view else 50,
                "sort_reverse": self._view.dust_reverse_sort_checkbox.isChecked() if self._view else True,
                "apparent_size": self._view.dust_apparent_size_checkbox.isChecked() if self._view else False,
                "min_size": self._view.dust_min_size_input.text() if self._view else "",
                "target_path": self._view.dust_target_path_input.text() if self._view else "",
                "include_types": self._view.dust_include_types_input.text() if self._view else "",
                "exclude_patterns": self._view.dust_exclude_patterns_input.text() if self._view else "",
            }
        except Exception as e:
            logger.error(f"Error getting dust settings: {e}")
            return {}

    def apply_settings(self, settings: Dict[str, Any]) -> None:
        if not self._view:
            return
        try:
            max_depth = settings.get("max_depth", 3)
            self._view.dust_max_depth_input.setValue(max_depth)

            number_of_lines = settings.get("number_of_lines", 50)
            self._view.dust_lines_input.setValue(number_of_lines)

            sort_reverse = settings.get("sort_reverse", True)
            self._view.dust_reverse_sort_checkbox.setChecked(sort_reverse)

            apparent_size = settings.get("apparent_size", False)
            self._view.dust_apparent_size_checkbox.setChecked(apparent_size)

            min_size = settings.get("min_size", "")
            self._view.dust_min_size_input.setText(min_size)

            target_path = settings.get("target_path", "")
            self._view.dust_path_input.setText(target_path)

            include_types = settings.get("include_types", "")
            self._view.dust_include_types_input.setText(include_types)

            exclude_patterns = settings.get("exclude_patterns", "")
            self._view.dust_exclude_patterns_input.setText(exclude_patterns)

            logger.info("Dust settings applied successfully")
        except Exception as e:
            logger.error(f"Error applying dust settings: {e}")

    # --- Operations ---
    def handle_directory_analysis(self, directory_path: str) -> bool:
        try:
            self._view.dust_target_path_input.setText(directory_path)
            logger.info(f"Directory analysis started in dust plugin: {directory_path}")
            return True
        except Exception as e:
            logger.error(f"Error handling directory analysis in dust plugin: {e}")
            return False

    def get_status_info(self) -> Dict[str, Any]:
        try:
            status_info = {
                "tool_available": self.check_tools_availability(),
                "current_directory": "",
                "cache_info": {},
            }

            if self._view:
                status_info["current_directory"] = self._view.dust_target_path_input.text()

            if self._model:
                status_info["cache_info"] = self._model.get_cache_info()

            return status_info
        except Exception as e:
            logger.error(f"Error getting dust status info: {e}")
            return {"error": str(e)}

    def execute_command(self, command: str, args: Dict[str, Any] | None = None) -> Any:
        args = args or {}
        try:
            if command == "analyze":
                directory = args.get("directory", "")
                if directory:
                    self._view.dust_target_path_input.setText(directory)
                self._controller._execute_analysis()
                return {"status": "analysis_started"}

            elif command == "check_tool":
                available, version, error = self._model.check_dust_availability()
                return {
                    "status": "tool_checked",
                    "available": available,
                    "version": version,
                    "error": error,
                }

            elif command == "clear_cache":
                self._view.dust_results_display.clear_results()
                return {"status": "cache_clear_started"}

            elif command == "set_depth":
                depth = args.get("depth", 3)
                self._view.dust_max_depth_input.setValue(depth)
                return {"status": f"depth_set_to_{depth}"}

            elif command == "set_limit":
                limit = args.get("limit", 50)
                self._view.dust_lines_input.setValue(limit)
                return {"status": f"limit_set_to_{limit}"}

            elif command == "analyze_directory":
                directory_path = args.get("directory_path", "")
                if directory_path:
                    self._view.dust_target_path_input.setText(directory_path)
                    return {"status": "directory_set", "directory_path": directory_path}
                return {"error": "No directory path provided"}

            else:
                return {"error": f"Unknown command: {command}"}
        except Exception as e:
            logger.error(f"Error executing dust command '{command}': {e}")
            return {"error": str(e)}

    def check_tools_availability(self) -> bool:
        try:
            available, _, _ = self._model.check_dust_availability()
            return available
        except Exception as e:
            logger.error(f"Error checking dust tool availability: {e}")
            return False
