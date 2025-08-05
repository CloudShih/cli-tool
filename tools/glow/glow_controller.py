"""
Glow Markdown 閱讀器的控制器層
協調 View 和 Model 之間的交互，處理用戶操作和業務邏輯
"""

import logging
from typing import Dict, Any
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QMessageBox

from .glow_model import GlowModel
from .glow_view import GlowView

logger = logging.getLogger(__name__)


class RenderWorker(QThread):
    """渲染工作線程，避免 UI 阻塞"""
    
    # 工作完成信號
    render_finished = pyqtSignal(bool, str, str, str)  # success, html_content, raw_output, error_message
    
    def __init__(self, model: GlowModel, render_params: Dict[str, Any]):
        super().__init__()
        self.model = model
        self.render_params = render_params
        self.is_cancelled = False
    
    def run(self):
        """執行渲染任務"""
        try:
            if self.is_cancelled:
                return
            
            # 從參數中提取資訊
            source = self.render_params.get('source', '')
            source_type = self.render_params.get('source_type', 'file')
            theme = self.render_params.get('theme', 'auto')
            width = self.render_params.get('width', 120)
            use_cache = self.render_params.get('use_cache', True)
            
            logger.info(f"Starting render task: {source_type} - {source[:100]}...")
            
            # 執行渲染
            success, html_content, error_message = self.model.render_markdown(
                source=source,
                source_type=source_type,
                theme=theme,
                width=width,
                use_cache=use_cache
            )
            
            if self.is_cancelled:
                return
            
            # 獲取原始輸出（簡化版，無樣式）
            raw_output = ""
            if success:
                # 嘗試獲取純文字版本
                try:
                    raw_success, raw_content, _ = self.model.render_markdown(
                        source=source,
                        source_type=source_type,
                        theme="notty",  # 無樣式主題
                        width=width,
                        use_cache=use_cache
                    )
                    if raw_success:
                        # 移除 HTML 標籤，提取純文字
                        from html import unescape
                        import re
                        raw_output = re.sub(r'<[^>]+>', '', raw_content)
                        raw_output = unescape(raw_output).strip()
                except Exception as e:
                    logger.warning(f"Failed to get raw output: {e}")
                    raw_output = "無法獲取原始輸出"
            
            # 調試信號發送前的數據
            logger.info(f"[DEBUG] RenderWorker about to emit signal:")
            logger.info(f"[DEBUG] - Success: {success}")
            logger.info(f"[DEBUG] - HTML length: {len(html_content)}")
            logger.info(f"[DEBUG] - HTML type: {type(html_content)}")
            logger.info(f"[DEBUG] - HTML preview: {html_content[:200]}...")
            logger.info(f"[DEBUG] - HTML contains <html>: {'<html>' in html_content}")
            logger.info(f"[DEBUG] - HTML contains <h1>: {'<h1' in html_content}")
            
            # 發送完成信號
            self.render_finished.emit(success, html_content, raw_output, error_message)
            
        except Exception as e:
            logger.error(f"Render worker error: {e}")
            self.render_finished.emit(False, "", "", f"渲染過程中發生錯誤: {str(e)}")
    
    def cancel(self):
        """取消渲染任務"""
        self.is_cancelled = True
        logger.info("Render task cancelled")


class ToolCheckWorker(QThread):
    """工具檢查工作線程"""
    
    # 檢查完成信號
    check_finished = pyqtSignal(bool, str, str)  # available, version_info, error_message
    
    def __init__(self, model: GlowModel):
        super().__init__()
        self.model = model
    
    def run(self):
        """執行工具可用性檢查"""
        try:
            logger.info("Checking Glow tool availability...")
            available, version_info, error_message = self.model.check_glow_availability()
            self.check_finished.emit(available, version_info, error_message)
        except Exception as e:
            logger.error(f"Tool check error: {e}")
            self.check_finished.emit(False, "", f"檢查工具時發生錯誤: {str(e)}")


class CacheWorker(QThread):
    """快取操作工作線程"""
    
    # 操作完成信號
    cache_operation_finished = pyqtSignal(bool, str, dict)  # success, message, cache_info
    
    def __init__(self, model: GlowModel, operation: str):
        super().__init__()
        self.model = model
        self.operation = operation  # "clear" or "info"
    
    def run(self):
        """執行快取操作"""
        try:
            if self.operation == "clear":
                success, message = self.model.clear_cache()
                cache_info = self.model.get_cache_info()
                self.cache_operation_finished.emit(success, message, cache_info)
            elif self.operation == "info":
                cache_info = self.model.get_cache_info()
                self.cache_operation_finished.emit(True, "快取信息已更新", cache_info)
        except Exception as e:
            logger.error(f"Cache operation error: {e}")
            self.cache_operation_finished.emit(False, f"快取操作發生錯誤: {str(e)}", {})


class GlowController(QObject):
    """Glow 工具的控制器，協調 View 和 Model"""
    
    def __init__(self, view: GlowView, model: GlowModel):
        super().__init__()
        self.view = view
        self.model = model
        
        # 工作線程
        self.render_worker = None
        self.tool_check_worker = None
        self.cache_worker = None
        
        # 連接信號和槽
        self._connect_signals()
        
        # 初始化快取信息
        self._update_cache_info()
        
        logger.info("GlowController initialized")
    
    def _connect_signals(self):
        """連接 View 的信號到對應的處理方法"""
        # 主要功能信號
        self.view.render_requested.connect(self._handle_render_request)
        self.view.check_glow_requested.connect(self._handle_check_glow_request)
        self.view.clear_cache_requested.connect(self._handle_clear_cache_request)
        
        # 檔案和輸入相關信號
        self.view.file_selected.connect(self._handle_file_selected)
        self.view.url_requested.connect(self._handle_url_request)
        self.view.text_input_requested.connect(self._handle_text_input_request)
        
        logger.info("Signals connected")
    
    def _handle_render_request(self, render_params: Dict[str, Any]):
        """處理渲染請求"""
        try:
            # 檢查是否已有渲染任務在執行
            if self.render_worker and self.render_worker.isRunning():
                logger.warning("Render task already running, cancelling previous task")
                self.render_worker.cancel()
                self.render_worker.wait(3000)  # 等待最多3秒
            
            # 更新 UI 狀態
            self.view.show_render_progress(True)
            self.view.update_status("working", "正在渲染 Markdown...")
            
            # 創建新的渲染工作線程
            self.render_worker = RenderWorker(self.model, render_params)
            self.render_worker.render_finished.connect(self._on_render_finished)
            self.render_worker.start()
            
            logger.info(f"Started render request: {render_params.get('source_type')} - {render_params.get('source', '')[:50]}...")
            
        except Exception as e:
            logger.error(f"Error handling render request: {e}")
            self.view.show_render_progress(False)
            self.view.update_status("error", f"渲染請求處理失敗: {str(e)}")
            self._show_error_message("渲染錯誤", f"處理渲染請求時發生錯誤:\n{str(e)}")
    
    def _on_render_finished(self, success: bool, html_content: str, raw_output: str, error_message: str):
        """渲染完成處理"""
        try:
            # 增強調試日誌
            logger.info(f"[DEBUG] Controller received signal:")
            logger.info(f"[DEBUG] - Success: {success}")
            logger.info(f"[DEBUG] - HTML content length: {len(html_content)}")
            logger.info(f"[DEBUG] - HTML content type: {type(html_content)}")
            logger.info(f"[DEBUG] - HTML content preview: {html_content[:200]}...")
            logger.info(f"[DEBUG] - HTML contains <html>: {'<html>' in html_content}")
            logger.info(f"[DEBUG] - HTML contains <h1>: {'<h1' in html_content}")
            logger.info(f"[DEBUG] - HTML contains <h2>: {'<h2' in html_content}")
            logger.info(f"[DEBUG] - Error message: {error_message}")
            
            # 更新 UI 狀態
            self.view.show_render_progress(False)
            
            if success:
                # 調試：記錄即將傳送到 View 的數據
                logger.info(f"[DEBUG] About to call view.update_preview_display with HTML length: {len(html_content)}")
                
                # 更新預覽顯示
                self.view.update_preview_display(html_content, raw_output)
                self.view.update_status("success", "Markdown 渲染完成")
                
                logger.info("[DEBUG] Render completed successfully")
            else:
                # 顯示錯誤
                self.view.update_status("error", "渲染失敗")
                self._show_error_message("渲染失敗", f"無法渲染 Markdown 內容:\n{error_message}")
                
                logger.error(f"[DEBUG] Render failed: {error_message}")
            
        except Exception as e:
            logger.error(f"[DEBUG] Error handling render completion: {e}")
            self.view.update_status("error", f"處理渲染結果時發生錯誤: {str(e)}")
    
    def _handle_check_glow_request(self):
        """處理 Glow 工具檢查請求"""
        try:
            # 檢查是否已有檢查任務在執行
            if self.tool_check_worker and self.tool_check_worker.isRunning():
                logger.warning("Tool check already running")
                return
            
            # 更新 UI 狀態
            self.view.update_status("working", "正在檢查 Glow 工具...")
            
            # 創建工具檢查工作線程
            self.tool_check_worker = ToolCheckWorker(self.model)
            self.tool_check_worker.check_finished.connect(self._on_tool_check_finished)
            self.tool_check_worker.start()
            
            logger.info("Started Glow tool check")
            
        except Exception as e:
            logger.error(f"Error handling tool check request: {e}")
            self.view.update_status("error", f"工具檢查請求處理失敗: {str(e)}")
    
    def _on_tool_check_finished(self, available: bool, version_info: str, error_message: str):
        """工具檢查完成處理"""
        try:
            if available:
                # Glow 可用
                self.view.update_status("success", f"Glow 工具可用: {version_info}")
                self._show_info_message(
                    "工具檢查", 
                    f"✅ Glow 工具已安裝並可正常使用\n\n版本信息: {version_info}"
                )
                logger.info(f"Glow tool available: {version_info}")
            else:
                # Glow 不可用
                self.view.update_status("error", "Glow 工具不可用")
                
                # 提供安裝指南
                install_guide = self._get_install_guide()
                self._show_error_message(
                    "工具不可用",
                    f"❌ Glow 工具未安裝或無法使用\n\n錯誤信息: {error_message}\n\n{install_guide}"
                )
                logger.error(f"Glow tool not available: {error_message}")
                
        except Exception as e:
            logger.error(f"Error handling tool check completion: {e}")
            self.view.update_status("error", f"處理工具檢查結果時發生錯誤: {str(e)}")
    
    def _handle_clear_cache_request(self):
        """處理清除快取請求"""
        try:
            # 確認操作
            reply = QMessageBox.question(
                self.view,
                "確認清除快取",
                "確定要清除所有快取檔案嗎？\n\n這將刪除所有已快取的遠程內容，下次載入時需要重新下載。",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 檢查是否已有快取操作在執行
                if self.cache_worker and self.cache_worker.isRunning():
                    logger.warning("Cache operation already running")
                    return
                
                # 更新 UI 狀態
                self.view.update_status("working", "正在清除快取...")
                
                # 創建快取操作工作線程
                self.cache_worker = CacheWorker(self.model, "clear")
                self.cache_worker.cache_operation_finished.connect(self._on_cache_operation_finished)
                self.cache_worker.start()
                
                logger.info("Started cache clear operation")
                
        except Exception as e:
            logger.error(f"Error handling clear cache request: {e}")
            self.view.update_status("error", f"清除快取請求處理失敗: {str(e)}")
    
    def _on_cache_operation_finished(self, success: bool, message: str, cache_info: Dict):
        """快取操作完成處理"""
        try:
            if success:
                self.view.update_status("success", message)
                self.view.update_cache_info(cache_info)
                
                # 顯示成功消息
                self._show_info_message("快取操作", f"✅ {message}")
                
                logger.info(f"Cache operation completed: {message}")
            else:
                self.view.update_status("error", "快取操作失敗")
                self._show_error_message("快取操作失敗", f"❌ {message}")
                
                logger.error(f"Cache operation failed: {message}")
                
        except Exception as e:
            logger.error(f"Error handling cache operation completion: {e}")
            self.view.update_status("error", f"處理快取操作結果時發生錯誤: {str(e)}")
    
    def _handle_file_selected(self, file_path: str):
        """處理檔案選擇"""
        try:
            # 獲取檔案信息
            file_info = self.model.get_file_info(file_path)
            
            if not file_info.get('exists', False):
                error_msg = file_info.get('error', '未知錯誤')
                self.view.update_status("error", f"檔案錯誤: {error_msg}")
                logger.warning(f"Selected file error: {error_msg}")
                return
            
            if not file_info.get('is_markdown', False):
                self.view.update_status("warning", "所選檔案可能不是 Markdown 格式")
                logger.warning(f"Selected file may not be markdown: {file_path}")
            else:
                self.view.update_status("ready", f"已選擇檔案: {file_info.get('name', '')}")
                logger.info(f"File selected: {file_path}")
                
        except Exception as e:
            logger.error(f"Error handling file selection: {e}")
            self.view.update_status("error", f"處理檔案選擇時發生錯誤: {str(e)}")
    
    def _handle_url_request(self, url: str):
        """處理 URL 請求"""
        try:
            # 驗證 URL
            is_valid, processed_url, error_message = self.model.validate_url(url)
            
            if is_valid:
                self.view.update_status("ready", f"URL 已驗證: {processed_url}")
                logger.info(f"URL validated: {url} -> {processed_url}")
            else:
                self.view.update_status("error", f"URL 無效: {error_message}")
                self._show_error_message("URL 錯誤", f"無效的 URL:\n{error_message}")
                logger.warning(f"Invalid URL: {url} - {error_message}")
                
        except Exception as e:
            logger.error(f"Error handling URL request: {e}")
            self.view.update_status("error", f"處理 URL 請求時發生錯誤: {str(e)}")
    
    def _handle_text_input_request(self, text: str):
        """處理文字輸入請求"""
        try:
            if text.strip():
                self.view.update_status("ready", f"已輸入文字內容 ({len(text)} 字符)")
                logger.info(f"Text input received: {len(text)} characters")
            else:
                self.view.update_status("ready", "文字輸入為空")
                
        except Exception as e:
            logger.error(f"Error handling text input request: {e}")
            self.view.update_status("error", f"處理文字輸入時發生錯誤: {str(e)}")
    
    def _update_cache_info(self):
        """更新快取信息"""
        try:
            # 檢查是否已有快取操作在執行
            if self.cache_worker and self.cache_worker.isRunning():
                return
            
            # 創建快取信息工作線程
            self.cache_worker = CacheWorker(self.model, "info")
            self.cache_worker.cache_operation_finished.connect(self._on_cache_info_updated)
            self.cache_worker.start()
            
        except Exception as e:
            logger.error(f"Error updating cache info: {e}")
    
    def _on_cache_info_updated(self, success: bool, message: str, cache_info: Dict):
        """快取信息更新完成"""
        if success:
            self.view.update_cache_info(cache_info)
            logger.debug("Cache info updated")
        else:
            logger.warning(f"Failed to update cache info: {message}")
    
    def _show_error_message(self, title: str, message: str):
        """顯示錯誤訊息對話框"""
        QMessageBox.critical(self.view, title, message)
    
    def _show_info_message(self, title: str, message: str):
        """顯示信息對話框"""
        QMessageBox.information(self.view, title, message)
    
    def _get_install_guide(self) -> str:
        """獲取 Glow 安裝指南"""
        return """
📦 Glow 安裝指南:

Windows:
• 使用 Scoop: scoop install glow
• 使用 Chocolatey: choco install glow
• 直接下載: https://github.com/charmbracelet/glow/releases

macOS:
• 使用 Homebrew: brew install glow
• 使用 MacPorts: sudo port install glow

Linux:
• 使用包管理器: apt install glow (Ubuntu/Debian)
• 使用 Snap: snap install glow
• 下載 deb/rpm 包: https://github.com/charmbracelet/glow/releases

Go 用戶:
• go install github.com/charmbracelet/glow@latest

安裝完成後，請重新點擊「檢查 Glow」按鈕進行驗證。
        """
    
    def cleanup(self):
        """清理資源"""
        try:
            # 停止所有工作線程
            if self.render_worker and self.render_worker.isRunning():
                self.render_worker.cancel()
                self.render_worker.wait(3000)
            
            if self.tool_check_worker and self.tool_check_worker.isRunning():
                self.tool_check_worker.terminate()
                self.tool_check_worker.wait(3000)
            
            if self.cache_worker and self.cache_worker.isRunning():
                self.cache_worker.terminate()
                self.cache_worker.wait(3000)
            
            logger.info("GlowController cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")