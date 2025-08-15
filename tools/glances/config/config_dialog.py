"""
Glances 配置對話框
提供用戶友好的配置界面
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QGroupBox, QLabel, QSpinBox, QCheckBox, QComboBox,
    QLineEdit, QPushButton, QDoubleSpinBox, QTextEdit,
    QFileDialog, QMessageBox, QFormLayout, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import logging
from pathlib import Path

from .config_manager import GlancesConfigManager

logger = logging.getLogger(__name__)


class ConfigDialog(QDialog):
    """配置對話框"""
    
    config_changed = pyqtSignal(dict)  # 配置變更信號
    
    def __init__(self, config_manager: GlancesConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("Glances 插件配置")
        self.setMinimumSize(600, 500)
        self.setup_ui()
        self.load_current_config()
        
        logger.info("ConfigDialog initialized")
        
    def setup_ui(self):
        """設置用戶界面"""
        layout = QVBoxLayout(self)
        
        # 標題
        title_label = QLabel("Glances 系統監控配置")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 標籤頁
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 創建各個配置標籤
        self.create_monitoring_tab()
        self.create_display_tab()
        self.create_connection_tab()
        self.create_alerts_tab()
        
        # 按鈕區域
        button_layout = self.create_button_layout()
        layout.addLayout(button_layout)
        
    def create_monitoring_tab(self):
        """創建監控配置標籤"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 基本監控設定
        basic_group = QGroupBox("基本監控設定")
        basic_layout = QFormLayout(basic_group)
        
        # 更新間隔
        self.update_interval_spin = QSpinBox()
        self.update_interval_spin.setRange(500, 60000)
        self.update_interval_spin.setSuffix(" ms")
        self.update_interval_spin.setValue(1000)
        basic_layout.addRow("更新間隔:", self.update_interval_spin)
        
        # 最大進程數
        self.max_processes_spin = QSpinBox()
        self.max_processes_spin.setRange(1, 100)
        self.max_processes_spin.setValue(20)
        basic_layout.addRow("最大進程數:", self.max_processes_spin)
        
        # 自動縮放
        self.auto_scale_check = QCheckBox("啟用圖表自動縮放")
        self.auto_scale_check.setChecked(True)
        basic_layout.addRow("圖表設定:", self.auto_scale_check)
        
        layout.addWidget(basic_group)
        
        # 圖表設定
        chart_group = QGroupBox("圖表設定")
        chart_layout = QFormLayout(chart_group)
        
        # 圖表時間範圍
        self.chart_range_spin = QSpinBox()
        self.chart_range_spin.setRange(10, 600)
        self.chart_range_spin.setSuffix(" 秒")
        self.chart_range_spin.setValue(60)
        chart_layout.addRow("時間範圍:", self.chart_range_spin)
        
        # 啟用圖表
        self.enable_charts_check = QCheckBox("啟用實時圖表")
        self.enable_charts_check.setChecked(True)
        chart_layout.addRow("圖表功能:", self.enable_charts_check)
        
        layout.addWidget(chart_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "監控設定")
        
    def create_display_tab(self):
        """創建顯示配置標籤"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 外觀設定
        appearance_group = QGroupBox("外觀設定")
        appearance_layout = QFormLayout(appearance_group)
        
        # 主題
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["default", "dark", "light"])
        appearance_layout.addRow("主題:", self.theme_combo)
        
        # 字體大小
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(10)
        appearance_layout.addRow("字體大小:", self.font_size_spin)
        
        layout.addWidget(appearance_group)
        
        # 圖表顯示設定
        chart_display_group = QGroupBox("圖表顯示")
        chart_display_layout = QFormLayout(chart_display_group)
        
        # 顯示網格
        self.show_grid_check = QCheckBox("顯示網格線")
        self.show_grid_check.setChecked(True)
        chart_display_layout.addRow("網格:", self.show_grid_check)
        
        # 顯示圖例
        self.show_legend_check = QCheckBox("顯示圖例")
        self.show_legend_check.setChecked(True)
        chart_display_layout.addRow("圖例:", self.show_legend_check)
        
        # 動畫效果
        self.animation_check = QCheckBox("啟用動畫效果")
        self.animation_check.setChecked(True)
        chart_display_layout.addRow("動畫:", self.animation_check)
        
        layout.addWidget(chart_display_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "顯示設定")
        
    def create_connection_tab(self):
        """創建連接配置標籤"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Web API 設定
        api_group = QGroupBox("Web API 設定")
        api_layout = QFormLayout(api_group)
        
        # API URL
        self.api_url_edit = QLineEdit()
        self.api_url_edit.setText("http://localhost:61208/api/3")
        api_layout.addRow("API URL:", self.api_url_edit)
        
        # 超時時間
        self.api_timeout_spin = QSpinBox()
        self.api_timeout_spin.setRange(1, 30)
        self.api_timeout_spin.setSuffix(" 秒")
        self.api_timeout_spin.setValue(5)
        api_layout.addRow("超時時間:", self.api_timeout_spin)
        
        # 重試次數
        self.api_retry_spin = QSpinBox()
        self.api_retry_spin.setRange(1, 10)
        self.api_retry_spin.setValue(3)
        api_layout.addRow("重試次數:", self.api_retry_spin)
        
        layout.addWidget(api_group)
        
        # 服務器設定
        server_group = QGroupBox("Glances 服務器")
        server_layout = QFormLayout(server_group)
        
        # 端口
        self.glances_port_spin = QSpinBox()
        self.glances_port_spin.setRange(1024, 65535)
        self.glances_port_spin.setValue(61208)
        server_layout.addRow("端口:", self.glances_port_spin)
        
        # 啟用回退模式
        self.fallback_check = QCheckBox("啟用回退模式")
        self.fallback_check.setChecked(True)
        server_layout.addRow("回退模式:", self.fallback_check)
        
        layout.addWidget(server_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "連接設定")
        
    def create_alerts_tab(self):
        """創建警告配置標籤"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 警告設定
        alert_group = QGroupBox("警告閾值設定")
        alert_layout = QFormLayout(alert_group)
        
        # 啟用警告
        self.enable_alerts_check = QCheckBox("啟用系統警告")
        self.enable_alerts_check.setChecked(True)
        alert_layout.addRow("警告功能:", self.enable_alerts_check)
        
        # CPU 閾值
        self.cpu_threshold_spin = QDoubleSpinBox()
        self.cpu_threshold_spin.setRange(0, 100)
        self.cpu_threshold_spin.setSuffix(" %")
        self.cpu_threshold_spin.setValue(80.0)
        alert_layout.addRow("CPU 警告閾值:", self.cpu_threshold_spin)
        
        # 記憶體閾值
        self.memory_threshold_spin = QDoubleSpinBox()
        self.memory_threshold_spin.setRange(0, 100)
        self.memory_threshold_spin.setSuffix(" %")
        self.memory_threshold_spin.setValue(85.0)
        alert_layout.addRow("記憶體警告閾值:", self.memory_threshold_spin)
        
        # 磁碟閾值
        self.disk_threshold_spin = QDoubleSpinBox()
        self.disk_threshold_spin.setRange(0, 100)
        self.disk_threshold_spin.setSuffix(" %")
        self.disk_threshold_spin.setValue(90.0)
        alert_layout.addRow("磁碟警告閾值:", self.disk_threshold_spin)
        
        layout.addWidget(alert_group)
        
        # 警告選項
        option_group = QGroupBox("警告選項")
        option_layout = QFormLayout(option_group)
        
        # 警告聲音
        self.alert_sound_check = QCheckBox("啟用警告聲音")
        self.alert_sound_check.setChecked(False)
        option_layout.addRow("聲音:", self.alert_sound_check)
        
        layout.addWidget(option_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "警告設定")
        
    def create_button_layout(self) -> QHBoxLayout:
        """創建按鈕區域"""
        layout = QHBoxLayout()
        
        # 導入/導出按鈕
        import_btn = QPushButton("導入配置")
        import_btn.clicked.connect(self.import_config)
        layout.addWidget(import_btn)
        
        export_btn = QPushButton("導出配置")
        export_btn.clicked.connect(self.export_config)
        layout.addWidget(export_btn)
        
        layout.addStretch()
        
        # 重置按鈕
        reset_btn = QPushButton("重置默認")
        reset_btn.clicked.connect(self.reset_to_defaults)
        layout.addWidget(reset_btn)
        
        # 確定/取消按鈕
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("確定")
        ok_btn.clicked.connect(self.accept_config)
        ok_btn.setDefault(True)
        layout.addWidget(ok_btn)
        
        return layout
        
    def load_current_config(self):
        """載入當前配置到界面"""
        # 監控配置
        monitoring = self.config_manager.get_monitoring_config()
        self.update_interval_spin.setValue(monitoring.update_interval)
        self.max_processes_spin.setValue(monitoring.max_processes)
        self.auto_scale_check.setChecked(monitoring.enable_auto_scale)
        self.chart_range_spin.setValue(monitoring.chart_range)
        self.enable_charts_check.setChecked(monitoring.enable_charts)
        
        # 顯示配置
        display = self.config_manager.get_display_config()
        self.theme_combo.setCurrentText(display.theme)
        self.font_size_spin.setValue(display.font_size)
        self.show_grid_check.setChecked(display.show_grid)
        self.show_legend_check.setChecked(display.show_legend)
        self.animation_check.setChecked(display.animation_enabled)
        
        # 連接配置
        connection = self.config_manager.get_connection_config()
        self.api_url_edit.setText(connection.web_api_url)
        self.api_timeout_spin.setValue(connection.web_api_timeout)
        self.api_retry_spin.setValue(connection.web_api_retry)
        self.glances_port_spin.setValue(connection.glances_port)
        self.fallback_check.setChecked(connection.fallback_enabled)
        
        # 警告配置
        alerts = self.config_manager.get_alert_config()
        self.enable_alerts_check.setChecked(alerts.enable_alerts)
        self.cpu_threshold_spin.setValue(alerts.cpu_threshold)
        self.memory_threshold_spin.setValue(alerts.memory_threshold)
        self.disk_threshold_spin.setValue(alerts.disk_threshold)
        self.alert_sound_check.setChecked(alerts.alert_sound)
        
    def accept_config(self):
        """確認並應用配置"""
        try:
            # 更新監控配置
            self.config_manager.update_monitoring_config(
                update_interval=self.update_interval_spin.value(),
                max_processes=self.max_processes_spin.value(),
                enable_auto_scale=self.auto_scale_check.isChecked(),
                chart_range=self.chart_range_spin.value(),
                enable_charts=self.enable_charts_check.isChecked()
            )
            
            # 更新顯示配置
            self.config_manager.update_display_config(
                theme=self.theme_combo.currentText(),
                font_size=self.font_size_spin.value(),
                show_grid=self.show_grid_check.isChecked(),
                show_legend=self.show_legend_check.isChecked(),
                animation_enabled=self.animation_check.isChecked()
            )
            
            # 更新連接配置
            self.config_manager.update_connection_config(
                web_api_url=self.api_url_edit.text(),
                web_api_timeout=self.api_timeout_spin.value(),
                web_api_retry=self.api_retry_spin.value(),
                glances_port=self.glances_port_spin.value(),
                fallback_enabled=self.fallback_check.isChecked()
            )
            
            # 更新警告配置
            self.config_manager.update_alert_config(
                enable_alerts=self.enable_alerts_check.isChecked(),
                cpu_threshold=self.cpu_threshold_spin.value(),
                memory_threshold=self.memory_threshold_spin.value(),
                disk_threshold=self.disk_threshold_spin.value(),
                alert_sound=self.alert_sound_check.isChecked()
            )
            
            # 驗證配置
            validation_errors = self.config_manager.validate_config()
            has_errors = any(errors for errors in validation_errors.values())
            
            if has_errors:
                error_msg = "配置驗證失敗:\n"
                for category, errors in validation_errors.items():
                    if errors:
                        error_msg += f"\n{category}:\n"
                        for error in errors:
                            error_msg += f"  - {error}\n"
                            
                QMessageBox.warning(self, "配置錯誤", error_msg)
                return
                
            # 發送配置變更信號
            config_summary = self.config_manager.get_config_summary()
            self.config_changed.emit(config_summary)
            
            QMessageBox.information(self, "成功", "配置已保存並應用")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"保存配置時發生錯誤:\n{str(e)}")
            
    def reset_to_defaults(self):
        """重置為默認配置"""
        reply = QMessageBox.question(
            self, "確認重置", 
            "確定要重置所有配置為默認值嗎？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.config_manager.reset_to_defaults()
            self.load_current_config()
            QMessageBox.information(self, "成功", "配置已重置為默認值")
            
    def import_config(self):
        """導入配置文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "導入配置文件", "", "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            success = self.config_manager.import_config(Path(file_path))
            if success:
                self.load_current_config()
                QMessageBox.information(self, "成功", "配置已成功導入")
            else:
                QMessageBox.critical(self, "錯誤", "導入配置失敗，請檢查文件格式")
                
    def export_config(self):
        """導出配置文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "導出配置文件", "glances_config.json", "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            success = self.config_manager.export_config(Path(file_path))
            if success:
                QMessageBox.information(self, "成功", f"配置已導出到:\n{file_path}")
            else:
                QMessageBox.critical(self, "錯誤", "導出配置失敗")