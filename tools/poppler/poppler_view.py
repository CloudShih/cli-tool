from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QPushButton, QTextEdit, QTabWidget,
    QLabel, QCheckBox, QComboBox, QSizePolicy, QFileDialog, QListWidget
)
from PyQt5.QtGui import QFont

class PopplerView(QWidget):
    def __init__(self):
        super().__init__()
        # Common font and stylesheet for results display
        self.results_font = QFont("Consolas", 12)
        self.results_stylesheet = "background-color: #282c34; color: #abb2bf;"

        main_layout = QVBoxLayout()
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # PDF Info Tab
        self.pdfinfo_tab = QWidget()
        self.tabs.addTab(self.pdfinfo_tab, "PDF 資訊")
        self._setup_pdfinfo_tab()

        # PDF to Text Tab
        self.pdftotext_tab = QWidget()
        self.tabs.addTab(self.pdftotext_tab, "PDF 轉文字")
        self._setup_pdftotext_tab()

        # PDF Images Tab
        self.pdfimages_tab = QWidget()
        self.tabs.addTab(self.pdfimages_tab, "提取圖片")
        self._setup_pdfimages_tab()

        # New: PDF Separate Tab
        self.pdfseparate_tab = QWidget()
        self.tabs.addTab(self.pdfseparate_tab, "分離頁面")
        self._setup_pdfseparate_tab()

        # New: PDF Unite Tab
        self.pdfunite_tab = QWidget()
        self.tabs.addTab(self.pdfunite_tab, "合併 PDF")
        self._setup_pdfunite_tab()

        

        # New: PDF to PPM Tab
        self.pdftoppm_tab = QWidget()
        self.tabs.addTab(self.pdftoppm_tab, "PDF 轉圖片")
        self._setup_pdftoppm_tab()

        

        self.setLayout(main_layout)

    def _setup_pdfinfo_tab(self):
        layout = QGridLayout()
        label_width = 180
        row = 0

        # PDF Path
        pdf_path_label = QLabel("PDF Path:")
        pdf_path_label.setMinimumWidth(label_width)
        layout.addWidget(pdf_path_label, row, 0)
        self.pdfinfo_path_input = QLineEdit()
        self.pdfinfo_path_input.setPlaceholderText("e.g., D:\\document.pdf")
        self.pdfinfo_path_input.setToolTip("輸入 PDF 檔案的絕對路徑。")
        layout.addWidget(self.pdfinfo_path_input, row, 1, 1, 10)
        
        self.pdfinfo_browse_button = QPushButton("瀏覽...")
        self.pdfinfo_browse_button.setToolTip("點擊以透過檔案總管選擇 PDF 檔案。")
        layout.addWidget(self.pdfinfo_browse_button, row, 11, 1, 2)
        row += 1

        # Get Info Button
        self.pdfinfo_get_info_button = QPushButton("Get PDF Info")
        layout.addWidget(self.pdfinfo_get_info_button, row, 0, 1, 12)
        row += 1

        # Results Display
        self.pdfinfo_results_display = QTextEdit()
        self.pdfinfo_results_display.setReadOnly(True)
        self.pdfinfo_results_display.setFont(self.results_font)
        self.pdfinfo_results_display.setStyleSheet(self.results_stylesheet)
        layout.addWidget(self.pdfinfo_results_display, row, 0, 1, 12)
        row += 1

        self.pdfinfo_tab.setLayout(layout)

    def _setup_pdftotext_tab(self):
        layout = QGridLayout()
        label_width = 180
        row = 0

        # PDF Path
        pdf_path_label = QLabel("PDF Path:")
        pdf_path_label.setMinimumWidth(label_width)
        layout.addWidget(pdf_path_label, row, 0)
        self.pdftotext_pdf_path_input = QLineEdit()
        self.pdftotext_pdf_path_input.setPlaceholderText("e.g., D:\\document.pdf")
        self.pdftotext_pdf_path_input.setToolTip("輸入 PDF 檔案的絕對路徑。")
        layout.addWidget(self.pdftotext_pdf_path_input, row, 1, 1, 10)
        
        self.pdftotext_browse_pdf_button = QPushButton("瀏覽 PDF...")
        self.pdftotext_browse_pdf_button.setToolTip("點擊以透過檔案總管選擇 PDF 檔案。")
        layout.addWidget(self.pdftotext_browse_pdf_button, row, 11, 1, 2)
        row += 1

        # Output Text Path
        output_path_label = QLabel("Output Text Path:")
        output_path_label.setMinimumWidth(label_width)
        layout.addWidget(output_path_label, row, 0)
        self.pdftotext_output_path_input = QLineEdit()
        self.pdftotext_output_path_input.setPlaceholderText("e.g., D:\\output.txt")
        self.pdftotext_output_path_input.setToolTip("輸入輸出文字檔案的絕對路徑。")
        layout.addWidget(self.pdftotext_output_path_input, row, 1, 1, 10)

        self.pdftotext_browse_output_button = QPushButton("瀏覽輸出...")
        self.pdftotext_browse_output_button.setToolTip("點擊以透過檔案總管選擇輸出文字檔案的路徑。")
        layout.addWidget(self.pdftotext_browse_output_button, row, 11, 1, 2)
        row += 1

        # Convert Button
        self.pdftotext_convert_button = QPushButton("Convert to Text")
        layout.addWidget(self.pdftotext_convert_button, row, 0, 1, 12)
        row += 1

        # Results Display
        self.pdftotext_results_display = QTextEdit()
        self.pdftotext_results_display.setReadOnly(True)
        self.pdftotext_results_display.setFont(self.results_font)
        self.pdftotext_results_display.setStyleSheet(self.results_stylesheet)
        layout.addWidget(self.pdftotext_results_display, row, 0, 1, 12)
        row += 1

        self.pdftotext_tab.setLayout(layout)

    def _setup_pdfimages_tab(self):
        layout = QGridLayout()
        label_width = 180
        row = 0

        # PDF Path
        pdf_path_label = QLabel("PDF Path:")
        pdf_path_label.setMinimumWidth(label_width)
        layout.addWidget(pdf_path_label, row, 0)
        self.pdfimages_pdf_path_input = QLineEdit()
        self.pdfimages_pdf_path_input.setPlaceholderText("e.g., D:\\document.pdf")
        self.pdfimages_pdf_path_input.setToolTip("輸入 PDF 檔案的絕對路徑。")
        layout.addWidget(self.pdfimages_pdf_path_input, row, 1, 1, 10)
        
        self.pdfimages_browse_pdf_button = QPushButton("瀏覽 PDF...")
        self.pdfimages_browse_pdf_button.setToolTip("點擊以透過檔案總管選擇 PDF 檔案。")
        layout.addWidget(self.pdfimages_browse_pdf_button, row, 11, 1, 2)
        row += 1

        # Output Directory
        output_dir_label = QLabel("Output Directory:")
        output_dir_label.setMinimumWidth(label_width)
        layout.addWidget(output_dir_label, row, 0)
        self.pdfimages_output_dir_input = QLineEdit()
        self.pdfimages_output_dir_input.setPlaceholderText("e.g., D:\\images")
        self.pdfimages_output_dir_input.setToolTip("輸入輸出圖片的目錄。")
        layout.addWidget(self.pdfimages_output_dir_input, row, 1, 1, 10)

        self.pdfimages_browse_output_dir_button = QPushButton("瀏覽目錄...")
        self.pdfimages_browse_output_dir_button.setToolTip("點擊以透過檔案總管選擇輸出圖片的目錄。")
        layout.addWidget(self.pdfimages_browse_output_dir_button, row, 11, 1, 2)
        row += 1

        # File Prefix
        file_prefix_label = QLabel("File Prefix:")
        file_prefix_label.setMinimumWidth(label_width)
        layout.addWidget(file_prefix_label, row, 0)
        self.pdfimages_file_prefix_input = QLineEdit()
        self.pdfimages_file_prefix_input.setPlaceholderText("e.g., img (default: img)")
        self.pdfimages_file_prefix_input.setToolTip("輸入輸出圖片檔案的前綴，預設為 'img'。")
        self.pdfimages_file_prefix_input.setText("img") # Set default value
        layout.addWidget(self.pdfimages_file_prefix_input, row, 1, 1, 10)
        row += 1

        # Image Format
        image_format_label = QLabel("Image Format:")
        image_format_label.setMinimumWidth(label_width)
        layout.addWidget(image_format_label, row, 0)
        self.pdfimages_format_combobox = QComboBox()
        self.pdfimages_format_combobox.addItem("png")
        self.pdfimages_format_combobox.addItem("ppm") # Added ppm
        self.pdfimages_format_combobox.setToolTip("選擇輸出圖片的格式，預設為 PNG。")
        layout.addWidget(self.pdfimages_format_combobox, row, 1)
        layout.setColumnStretch(2, 1) # Stretch the third column to push content left
        row += 1

        # Extract Button
        self.pdfimages_extract_button = QPushButton("Extract Images")
        layout.addWidget(self.pdfimages_extract_button, row, 0, 1, 12)
        row += 1

        # Results Display
        self.pdfimages_results_display = QTextEdit()
        self.pdfimages_results_display.setReadOnly(True)
        self.pdfimages_results_display.setFont(self.results_font)
        self.pdfimages_results_display.setStyleSheet(self.results_stylesheet)
        layout.addWidget(self.pdfimages_results_display, row, 0, 1, 12)
        row += 1

        self.pdfimages_tab.setLayout(layout)

    # New placeholder setup methods for other Poppler tools
    def _setup_pdfseparate_tab(self):
        layout = QGridLayout()
        label_width = 180
        row = 0

        # PDF Path
        pdf_path_label = QLabel("PDF Path:")
        pdf_path_label.setMinimumWidth(label_width)
        layout.addWidget(pdf_path_label, row, 0)
        self.pdfseparate_pdf_path_input = QLineEdit()
        self.pdfseparate_pdf_path_input.setPlaceholderText("e.g., D:\\document.pdf")
        self.pdfseparate_pdf_path_input.setToolTip("輸入 PDF 檔案的絕對路徑。")
        layout.addWidget(self.pdfseparate_pdf_path_input, row, 1, 1, 10)
        
        self.pdfseparate_browse_pdf_button = QPushButton("瀏覽 PDF...")
        self.pdfseparate_browse_pdf_button.setToolTip("點擊以透過檔案總管選擇 PDF 檔案。")
        layout.addWidget(self.pdfseparate_browse_pdf_button, row, 11, 1, 2)
        row += 1

        # Output Directory
        output_dir_label = QLabel("Output Directory:")
        output_dir_label.setMinimumWidth(label_width)
        layout.addWidget(output_dir_label, row, 0)
        self.pdfseparate_output_dir_input = QLineEdit()
        self.pdfseparate_output_dir_input.setPlaceholderText("e.g., D:\\output_folder")
        self.pdfseparate_output_dir_input.setToolTip("選擇存放分離後 PDF 檔案的資料夾。")
        layout.addWidget(self.pdfseparate_output_dir_input, row, 1, 1, 10)

        self.pdfseparate_browse_output_button = QPushButton("瀏覽目錄...")
        self.pdfseparate_browse_output_button.setToolTip("點擊以透過檔案總管選擇輸出資料夾。")
        layout.addWidget(self.pdfseparate_browse_output_button, row, 11, 1, 2)
        row += 1

        # Separate Button
        self.pdfseparate_separate_button = QPushButton("Separate PDF")
        layout.addWidget(self.pdfseparate_separate_button, row, 0, 1, 12)
        row += 1

        # Results Display
        self.pdfseparate_results_display = QTextEdit()
        self.pdfseparate_results_display.setReadOnly(True)
        self.pdfseparate_results_display.setFont(self.results_font)
        self.pdfseparate_results_display.setStyleSheet(self.results_stylesheet)
        layout.addWidget(self.pdfseparate_results_display, row, 0, 1, 12)
        row += 1

        self.pdfseparate_tab.setLayout(layout)

    def _setup_pdfunite_tab(self):
        layout = QGridLayout()
        row = 0

        # File List
        self.pdfunite_file_list = QListWidget()
        self.pdfunite_file_list.setToolTip("要合併的 PDF 檔案列表。")
        layout.addWidget(self.pdfunite_file_list, row, 0, 1, 12)
        row += 1

        # Action Buttons
        button_layout = QHBoxLayout()
        self.pdfunite_add_button = QPushButton("新增檔案")
        self.pdfunite_add_button.setToolTip("新增要合併的 PDF 檔案。")
        button_layout.addWidget(self.pdfunite_add_button)

        self.pdfunite_remove_button = QPushButton("移除選取")
        self.pdfunite_remove_button.setToolTip("從列表中移除選取的檔案。")
        button_layout.addWidget(self.pdfunite_remove_button)

        self.pdfunite_move_up_button = QPushButton("上移")
        self.pdfunite_move_up_button.setToolTip("將選取的檔案在列表中向上移動。")
        button_layout.addWidget(self.pdfunite_move_up_button)

        self.pdfunite_move_down_button = QPushButton("下移")
        self.pdfunite_move_down_button.setToolTip("將選取的檔案在列表中向下移動。")
        button_layout.addWidget(self.pdfunite_move_down_button)
        
        layout.addLayout(button_layout, row, 0, 1, 12)
        row += 1

        # Output Path
        output_path_label = QLabel("輸出檔案路徑:")
        layout.addWidget(output_path_label, row, 0)
        self.pdfunite_output_path_input = QLineEdit()
        self.pdfunite_output_path_input.setPlaceholderText("e.g., D:\\merged.pdf")
        self.pdfunite_output_path_input.setToolTip("設定合併後 PDF 的儲存路徑與檔名。")
        layout.addWidget(self.pdfunite_output_path_input, row, 1, 1, 10)

        self.pdfunite_browse_output_button = QPushButton("瀏覽...")
        self.pdfunite_browse_output_button.setToolTip("選擇輸出路徑。")
        layout.addWidget(self.pdfunite_browse_output_button, row, 11, 1, 2)
        row += 1

        # Unite Button
        self.pdfunite_unite_button = QPushButton("合併 PDF")
        layout.addWidget(self.pdfunite_unite_button, row, 0, 1, 12)
        row += 1

        # Results Display
        self.pdfunite_results_display = QTextEdit()
        self.pdfunite_results_display.setReadOnly(True)
        self.pdfunite_results_display.setFont(self.results_font)
        self.pdfunite_results_display.setStyleSheet(self.results_stylesheet)
        layout.addWidget(self.pdfunite_results_display, row, 0, 1, 12)
        row += 1

        self.pdfunite_tab.setLayout(layout)

    

    def _setup_pdftoppm_tab(self):
        layout = QGridLayout()
        label_width = 180
        row = 0

        # PDF Path
        pdf_path_label = QLabel("PDF Path:")
        pdf_path_label.setMinimumWidth(label_width)
        layout.addWidget(pdf_path_label, row, 0)
        self.pdftoppm_pdf_path_input = QLineEdit()
        self.pdftoppm_pdf_path_input.setPlaceholderText("e.g., D:\\document.pdf")
        self.pdftoppm_pdf_path_input.setToolTip("輸入 PDF 檔案的絕對路徑。")
        layout.addWidget(self.pdftoppm_pdf_path_input, row, 1, 1, 10)
        
        self.pdftoppm_browse_pdf_button = QPushButton("瀏覽 PDF...")
        self.pdftoppm_browse_pdf_button.setToolTip("點擊以透過檔案總管選擇 PDF 檔案。")
        layout.addWidget(self.pdftoppm_browse_pdf_button, row, 11, 1, 2)
        row += 1

        # Output Directory
        output_dir_label = QLabel("Output Directory:")
        output_dir_label.setMinimumWidth(label_width)
        layout.addWidget(output_dir_label, row, 0)
        self.pdftoppm_output_dir_input = QLineEdit()
        self.pdftoppm_output_dir_input.setPlaceholderText("e.g., D:\\images")
        self.pdftoppm_output_dir_input.setToolTip("輸入輸出圖片的目錄。")
        layout.addWidget(self.pdftoppm_output_dir_input, row, 1, 1, 10)

        self.pdftoppm_browse_output_button = QPushButton("瀏覽目錄...")
        self.pdftoppm_browse_output_button.setToolTip("點擊以透過檔案總管選擇輸出圖片的目錄。")
        layout.addWidget(self.pdftoppm_browse_output_button, row, 11, 1, 2)
        row += 1

        # File Prefix
        file_prefix_label = QLabel("File Prefix:")
        file_prefix_label.setMinimumWidth(label_width)
        layout.addWidget(file_prefix_label, row, 0)
        self.pdftoppm_file_prefix_input = QLineEdit()
        self.pdftoppm_file_prefix_input.setPlaceholderText("e.g., page (default: page)")
        self.pdftoppm_file_prefix_input.setToolTip("輸入輸出圖片檔案的前綴，預設為 'page'。")
        self.pdftoppm_file_prefix_input.setText("page") # Set default value
        layout.addWidget(self.pdftoppm_file_prefix_input, row, 1, 1, 10)
        row += 1

        # Image Format
        image_format_label = QLabel("Image Format:")
        image_format_label.setMinimumWidth(label_width)
        layout.addWidget(image_format_label, row, 0)
        self.pdftoppm_format_combobox = QComboBox()
        self.pdftoppm_format_combobox.addItem("ppm")
        self.pdftoppm_format_combobox.addItem("png")
        self.pdftoppm_format_combobox.addItem("jpeg")
        self.pdftoppm_format_combobox.setToolTip("選擇輸出圖片的格式，預設為 PPM。")
        layout.addWidget(self.pdftoppm_format_combobox, row, 1)
        layout.setColumnStretch(2, 1) # Stretch the third column to push content left
        row += 1

        # Page Range
        page_range_label = QLabel("Page Range (Start-End):")
        page_range_label.setMinimumWidth(label_width)
        layout.addWidget(page_range_label, row, 0)
        self.pdftoppm_start_page_input = QLineEdit()
        self.pdftoppm_start_page_input.setPlaceholderText("Start Page (optional)")
        self.pdftoppm_start_page_input.setToolTip("輸入起始頁碼 (可選)。")
        layout.addWidget(self.pdftoppm_start_page_input, row, 1, 1, 5)
        self.pdftoppm_end_page_input = QLineEdit()
        self.pdftoppm_end_page_input.setPlaceholderText("End Page (optional)")
        self.pdftoppm_end_page_input.setToolTip("輸入結束頁碼 (可選)。")
        layout.addWidget(self.pdftoppm_end_page_input, row, 6, 1, 5)
        row += 1

        # Convert Button
        self.pdftoppm_convert_button = QPushButton("Convert to PPM")
        layout.addWidget(self.pdftoppm_convert_button, row, 0, 1, 12)
        row += 1

        # Results Display
        self.pdftoppm_results_display = QTextEdit()
        self.pdftoppm_results_display.setReadOnly(True)
        self.pdftoppm_results_display.setFont(self.results_font)
        self.pdftoppm_results_display.setStyleSheet(self.results_stylesheet)
        layout.addWidget(self.pdftoppm_results_display, row, 0, 1, 12)
        row += 1

        self.pdftoppm_tab.setLayout(layout)

    