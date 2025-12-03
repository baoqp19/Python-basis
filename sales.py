import sys
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QListWidget, QTextEdit, QVBoxLayout, QHBoxLayout,
    QFrame, QMessageBox, QSplitter
)
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt, QSize


class SalesClass(QWidget):
    def __init__(self):
        super().__init__()
        self.txt_invoice = None
        self.setWindowTitle("Hệ Thống Quản Lý Kho | Xem Hóa Đơn Khách Hàng")
        self.setGeometry(200, 100, 1200, 700)
        self.setMinimumSize(1000, 600)

        # Danh sách invoice (chỉ lưu tên file không có .txt)
        self.bill_list = []
        self.bill_folder = r"D:\ALL_PROJECT\Python\Inventory-Management-System\bill"

        self.init_ui()
        self.load_bill_list()

    def init_ui(self):
        # ===================== TOÀN BỘ THIẾT KẾ ĐỈNH CAO - NỀN TRẮNG + CHỮ ĐEN =====================
        self.setStyleSheet("""
            QWidget {
                background-color: #f9f9fb;
                color: #1a1a1a;
                font-family: "Segoe UI", "Roboto", sans-serif;
            }
            QLabel {
                color: #2d2d2d;
                font-weight: 600;
            }
            QLineEdit {
                background-color: #ffffff;
                color: #000000;
                border: 2px solid #d0d0d0;
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 15px;
                selection-background-color: #0066cc;
            }
            QLineEdit:focus {
                border: 2px solid #0066cc;
                background-color: #f8fbff;
            }
            QLineEdit::placeholder {
                color: #888888;
            }
            QPushButton {
                background-color: #0066cc;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 28px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0055b3;
            }
            QPushButton:pressed {
                background-color: #004494;
            }
            QPushButton#clearBtn {
                background-color: #f1f3f5;
                color: #333333;
                border: 2px solid #ced4da;
                font-weight: normal;
            }
            QPushButton#clearBtn:hover {
                background-color: #e2e6ea;
                border: 2px solid #adb5bd;
            }
            QListWidget {
                background-color: #ffffff;
                border: 2px solid #e0e0e0;
                border-radius: 14px;
                padding: 8px;
                font-size: 14px;
                outline: none;
            }
            QListWidget::item {
                padding: 14px 16px;
                border-radius: 10px;
                margin: 4px 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #0066cc;
                color: white;
                font-weight: bold;
            }
            QListWidget::item:hover:!selected {
                background-color: #f0f7ff;
                border-radius: 10px;
            }
            QTextEdit {
                background-color: #ffffff;
                color: #000000;
                border: 2px solid #e0e0e0;
                border-radius: 14px;
                padding: 20px;
                font-family: "Consolas", "Courier New", monospace;
                font-size: 13.5px;
                line-height: 1.6;
            }
            QFrame {
                background-color: white;
                border-radius: 16px;
                border: 1px solid #e8e8e8;
            }
            QSplitter::handle {
                background-color: #d0d0d0;
                width: 6px;
                border-radius: 3px;
            }
        """)

        # ===================== TIÊU ĐỀ SIÊU ĐẸP =====================
        title = QLabel("XEM HÓA ĐƠN KHÁCH HÀNG")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #0066cc, stop:0.5 #0077ee, stop:1 #0088ff);
            color: white;
            padding: 24px;
            border-radius: 16px;
            margin: 20px 20px 10px 20px;
            font-weight: bold;
            letter-spacing: 1px;
        """)

        # ===================== THANH TÌM KIẾM - SIÊU MƯỢT =====================
        search_frame = QFrame()
        search_frame.setStyleSheet("""
            background: white;
            border-radius: 16px;
            border: 1px solid #e0e0e0;
            padding: 20px;
            margin: 0px 20px 20px 20px;
        """)
        search_layout = QHBoxLayout(search_frame)
        search_layout.setSpacing(16)
        search_layout.setContentsMargins(10, 10, 10, 10)

        lbl_search = QLabel("Số hóa đơn:")
        lbl_search.setFont(QFont("Segoe UI", 13, QFont.Bold))

        self.txt_invoice = QLineEdit()
        self.txt_invoice.setPlaceholderText("Nhập số hóa đơn...")
        self.txt_invoice.setFixedHeight(80)

        # Tạo 2 nút
        btn_search = QPushButton("TÌM KIẾM")
        btn_clear = QPushButton("LÀM MỚI")

        # Cấu hình cơ bản
        btn_clear.setObjectName("clearBtn")  # để CSS riêng cho nút LÀM MỚI
        btn_search.setFixedHeight(70)
        btn_clear.setFixedHeight(80)
        btn_search.setMinimumWidth(140)  # cho đẹp, không bị co quá
        btn_clear.setMinimumWidth(140)

        # Áp dụng CSS siêu đẹp + chữ đen 100%
        btn_search.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #000000;                    
                border: 2.5px solid #3b82f6;       
                border-radius: 14px;
                font-weight: bold;
                font-size: 15px;
                font-family: Segoe UI, Arial, sans-serif;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background-color: #eff6ff;
                border-color: #2563eb;
                box-shadow: 0 6px 20px rgba(59, 131, 246, 0.3);
            }
            QPushButton:pressed {
                background-color: #dbeafe;
                transform: translateY(2px);
            }

            /* Nút LÀM MỚI - xanh lá nhẹ nhàng, dễ phân biệt */
            QPushButton#clearBtn {
                background-color: #f0fdf4;
                border: 2.5px solid #22c55e;
                color: #000000;
            }
            QPushButton#clearBtn:hover {
                background-color: #dcfce7;
                border-color: #16a34a;
                box-shadow: 0 6px 20px rgba(34, 197, 94, 0.3);
            }
            QPushButton#clearBtn:pressed {
                background-color: #bbf7d0;
                transform: translateY(2px);
            }
        """)

        btn_search.setCursor(Qt.PointingHandCursor)
        btn_clear.setCursor(Qt.PointingHandCursor)

        btn_search.clicked.connect(self.search)
        btn_clear.clicked.connect(self.clear)

        search_layout.addWidget(lbl_search)
        search_layout.addWidget(self.txt_invoice, 1)
        search_layout.addWidget(btn_search)
        search_layout.addWidget(btn_clear)

        # ===================== NỘI DUNG CHÍNH =====================
        splitter = QSplitter(Qt.Horizontal)

        # --- Danh sách hóa đơn ---
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(15)
        left_layout.addWidget(QLabel("DANH SÁCH HÓA ĐƠN"))
        self.list_bills = QListWidget()
        self.list_bills.itemClicked.connect(self.on_bill_selected)
        left_layout.addWidget(self.list_bills)

        # --- Nội dung hóa đơn ---
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(15)
        right_layout.addWidget(QLabel("NỘI DUNG HÓA ĐƠN"))
        self.bill_display = QTextEdit()
        self.bill_display.setReadOnly(True)
        right_layout.addWidget(self.bill_display)

        # --- Ảnh trang trí ---
        image_label = QLabel()
        pixmap = QPixmap(r"D:\ALL_PROJECT\Python\Inventory-Management-System/images/cat2.jpg")
        if not pixmap.isNull():
            scaled = pixmap.scaled(440, 340, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(scaled)
            image_label.setStyleSheet("""
                background: white;
                border-radius: 20px;
                padding: 15px;
                border: 1px solid #e0e0e0;
            """)
        image_label.setAlignment(Qt.AlignCenter)

        splitter.addWidget(left_frame)
        splitter.addWidget(right_frame)
        splitter.addWidget(image_label)
        splitter.setSizes([340, 540, 340])

        # ===================== LAYOUT TỔNG THỂ =====================
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(title)
        main_layout.addWidget(search_frame)
        main_layout.addWidget(splitter, 1)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(12, 12, 12, 12)

    def load_bill_list(self):
        self.list_bills.clear()
        self.bill_list.clear()

        if not os.path.exists(self.bill_folder):
            self.list_bills.addItem("Thư mục bill không tồn tại!")
            return

        files = [f for f in os.listdir(self.bill_folder) if f.endswith('.txt')]
        if not files:
            self.list_bills.addItem("Chưa có hóa đơn nào.")
            return

        files.sort(reverse=True)  # mới nhất lên đầu
        for file in files:
            invoice_no = file.replace('.txt', '')
            self.bill_list.append(invoice_no)
            self.list_bills.addItem(invoice_no)

    def on_bill_selected(self, item):
        invoice_no = item.text()
        self.display_bill(invoice_no)

    def display_bill(self, invoice_no):
        file_path = os.path.join(self.bill_folder, f"{invoice_no}.txt")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.bill_display.setPlainText(content)
            self.txt_invoice.setText(invoice_no)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể đọc file:\n{e}")

    def search(self):
        invoice = self.txt_invoice.text().strip()
        if not invoice:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập số hóa đơn!")
            return

        if invoice in self.bill_list:
            self.display_bill(invoice)
            # Highlight item trong list
            items = self.list_bills.findItems(invoice, Qt.MatchExactly)
            if items:
                self.list_bills.setCurrentItem(items[0])
        else:
            QMessageBox.warning(self, "Không tìm thấy", "Không tồn tại hóa đơn này!")

    def clear(self):
        self.txt_invoice.clear()
        self.bill_display.clear()
        self.list_bills.clearSelection()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # giao diện đẹp hơn
    window = SalesClass()
    window.show()
    sys.exit(app.exec())