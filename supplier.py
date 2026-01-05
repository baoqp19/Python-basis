import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QGridLayout,
    QHeaderView, QGraphicsDropShadowEffect, QMessageBox
)
from PySide6.QtGui import QFont, QColor
import mysql.connector
from Toast import *

# ============================= CONFIRM DIALOG ĐẸP =============================
class ConfirmDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(400, 220)

        self.setStyleSheet("background: rgba(255,255,255,245); border-radius: 16px;")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0,0,0,100))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        icon = QLabel("Warning")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size: 48px;")
        layout.addWidget(icon)

        title = QLabel("Xóa nhà cung cấp?")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        desc = QLabel("Dữ liệu sẽ <b>không thể khôi phục</b> sau khi xóa.")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #666;")
        layout.addWidget(desc)

        btns = QHBoxLayout()
        btns.addStretch()

        self.btn_no = QPushButton("Hủy bỏ")
        self.btn_yes = QPushButton("Xóa ngay")
        self.btn_yes.setDefault(True)

        for b in (self.btn_no, self.btn_yes):
            b.setFixedSize(120, 44)
            b.setFont(QFont("Segoe UI", 11, QFont.Bold))
            b.setCursor(Qt.PointingHandCursor)

        self.btn_no.setStyleSheet("background:#6c757d; color:white; border-radius:10px;")
        self.btn_yes.setStyle("background:#e74c3c; color:white; border-radius:10px;")
        self.btn_yes.setStyleSheet("""
            QPushButton { background:#e74c3c; color:white; border-radius:10px; }
            QPushButton:hover { background:#c0392b; }
        """)

        btns.addWidget(self.btn_no)
        btns.addWidget(self.btn_yes)
        layout.addLayout(btns)

        self.btn_yes.clicked.connect(self.accept)
        self.btn_no.clicked.connect(self.reject)

    def exec(self):
        parent = self.parent()
        px = parent.x() + (parent.width() - self.width()) // 2
        py = parent.y() + (parent.height() - self.height()) // 2

        start = QRect(px, py + 80, self.width(), self.height())
        end = QRect(px, py, self.width(), self.height())
        self.setGeometry(start)

        anim = QPropertyAnimation(self, b"geometry")
        anim.setDuration(400)
        anim.setEasingCurve(QEasingCurve.OutBack)
        anim.setStartValue(start)
        anim.setEndValue(end)
        self.show()
        anim.start()

        self.result = False
        self.loop = QTimer()
        self.loop.start(50)
        while self.isVisible():
            QApplication.processEvents()
        return self.result

    def accept(self): self.result = True; self.close_anim()
    def reject(self): self.result = False; self.close_anim()

    def close_anim(self):
        anim = QPropertyAnimation(self, b"geometry")
        anim.setDuration(300)
        anim.setEasingCurve(QEasingCurve.InBack)
        anim.setStartValue(self.geometry())
        anim.setEndValue(QRect(self.x(), self.y() + 80, self.width(), self.height()))
        anim.finished.connect(self.close)
        anim.start()


# ============================= SUPPLIER WINDOW =============================
class SupplierWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản Lý Nhà Cung Cấp")
        self.setGeometry(300, 150, 1100, 650)
        self.setStyleSheet("background-color: #f8f9fa;")
        self.setup_ui()
        self.connect_db()
        self.load_data()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Title
        title = QLabel("QUẢN LÝ NHÀ CUNG CẤP")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #0d6efd; padding: 15px; background: white; border-radius: 12px;")
        main_layout.addWidget(title)

        content = QHBoxLayout()
        content.setSpacing(25)

        # === LEFT: Form ===
        left = QVBoxLayout()
        left.setSpacing(15)

        self.var_sup_invoice = QLineEdit()
        self.var_name = QLineEdit()
        self.var_contact = QLineEdit()
        self.txt_desc = QTextEdit()

        # GÁN PLACEHOLDER RIÊNG CHO TỪNG Ô
        self.var_sup_invoice.setPlaceholderText("VD: 001, 002...")
        self.var_name.setPlaceholderText("Nhập tên nhà cung cấp")
        self.var_contact.setPlaceholderText("Số điện thoại hoặc email")
        self.txt_desc.setPlaceholderText("Ghi chú thêm về nhà cung cấp, điều khoản thanh toán, v.v...")

        fields = [
            ("Mã nhà cung cấp", self.var_sup_invoice),
            ("Tên nhà cung cấp", self.var_name),
            ("Số điện thoại", self.var_contact),
            ("Mô tả", self.txt_desc),
        ]

        # CSS chung đẹp + placeholder màu xám đậm (rõ hơn mặc định)
        input_style = """
            QLineEdit, QTextEdit {
                background-color: white;
                color: black;
                font-size: 14px;
                font-weight: 500;
                border: 2.5px solid #ced4da;
                border-radius: 12px;
                padding: 10px 14px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 2.5px solid #3498db;
                background-color: #f8fbff;
            }
            QLineEdit:hover, QTextEdit:hover {
                border: 2.5px solid #74b9ff;
            }
            QLineEdit::placeholder, QTextEdit::placeholder {
                color: #6c757d;              /* xám đậm, dễ đọc */
                font-weight: 400;
                font-style: italic;
            }
        """

        for label_text, widget in fields:
            lbl = QLabel(label_text)
            lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
            lbl.setStyleSheet("color: #212529;")
            left.addWidget(lbl)

            # Chiều cao cố định
            if isinstance(widget, QTextEdit):
                widget.setFixedHeight(100)
            else:
                widget.setFixedHeight(48)

            # Áp dụng CSS chung
            widget.setStyleSheet(input_style)
            left.addWidget(widget)

        left.addStretch()

        # Buttons
        btns = QHBoxLayout()

        buttons = [
            ("Lưu", "#0d6efd", self.add),
            ("Sửa", "#198754", self.update),
            ("Xóa", "#dc3545", self.delete_supplier),
            ("Làm mới", "#6c757d", self.clear),
        ]

        for text, color, func in buttons:
            b = QPushButton(text)
            b.setFixedSize(120, 45)
            b.setStyleSheet(f"""
                QPushButton {{ background:{color}; color:white; font-weight:bold; border-radius:10px; }}
                QPushButton:hover {{ background: {self.darken(color)}; }}
            """)
            b.clicked.connect(func)
            btns.addWidget(b)
        left.addLayout(btns)

        # === RIGHT: Search + Table ===
        right = QVBoxLayout()

        search_bar = QHBoxLayout()
        search_bar.addWidget(QLabel("Tìm kiếm nhà cung cấp:"))

        # Dòng này thêm vào ngay sau là xong!
        search_bar.itemAt(0).widget().setStyleSheet("""
            QLabel {
                color: black;                    
                font-size: 14px;
                font-weight: 600;
                padding: 0px 8px 0px 0px;
            }
        """)
        self.var_searchtxt = QLineEdit()
        self.var_searchtxt.setFixedHeight(45)
        self.var_searchtxt.setStyleSheet("""
            QLineEdit {
                border: 2px solid #dee2e6;
                border-radius: 10px;
                padding: 0 15px;
                background-color: white;   /* nền trắng để chắc chắn */
                color: black;              /* chữ đen 100% */
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #fd79a8;  /* hồng Shopee khi focus (tuỳ chọn) */
            }
        """)
        btn_search = QPushButton("Tìm")
        btn_search.setFixedHeight(45)
        btn_search.setCursor(Qt.CursorShape.PointingHandCursor)  # con trỏ tay khi hover

        # CSS siêu đẹp cho nút Tìm
        btn_search.setStyleSheet("""
            QPushButton {
                background-color: #3498db;        /* màu xanh dương đẹp */
                color: white;                     /* chữ trắng mặc định */
                border-radius: 8px;               /* bo góc */
                font-size: 14px;
                font-weight: bold;
                padding: 0px 20px;                /* khoảng cách chữ trong nút */
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;        /* đậm hơn khi hover */
            }
            QPushButton:pressed {
                background-color: #1c6ea4;        /* nhấn xuống thì tối hơn */
            }
            QPushButton:focus {
                outline: none;                    /* bỏ viền focus mặc định */
            }
        """)

        # Nếu bạn MUỐN CHỮ MÀU ĐEN thì dùng cái này thay phần trên:
        btn_search.setStyleSheet("""
            QPushButton {
                background-color: #f1c40f;        /* nền vàng tươi (hoặc #2ecc71 xanh lá, #e74c3c đỏ...) */
                color: black;                     /* CHỮ MÀU ĐEN */
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
                font-family: Segoe UI, Arial;
                padding: 8px 24px;
                border: 2px solid #d4ac0d;        /* viền vàng đậm hơn chút */
            }
            QPushButton:hover {
                background-color: #f39c12;
                border: 2px solid #e67e22;
            }
            QPushButton:pressed {
                background-color: #e67e22;
            }
        """)

        btn_search.clicked.connect(self.search)
        search_bar.addWidget(self.var_searchtxt)
        search_bar.addWidget(btn_search)
        right.addLayout(search_bar)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Mã HĐ", "Tên NCC", "Liên hệ", "Mô tả"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #dee2e6;
                font-size: 13px;
                color: black;                    /* Dòng quan trọng nhất: chữ đen */
                alternate-background-color: #f8f9fa;
                selection-background-color: #007bff;
                selection-color: white;
            }
            QTableWidget::item {
                color: black;                    /* Đảm bảo 100% chữ đen */
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #0d6efd;
                color: white;
            }
            QHeaderView::section {
                background-color: #0d6efd;
                color: white;
                font-weight: bold;
                padding: 12px;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f1f1;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #adb5bd;
                border-radius: 5px;
            }
        """)

        self.table.cellClicked.connect(self.table_to_form)
        right.addWidget(self.table)

        content.addLayout(left, 2)
        content.addLayout(right, 3)
        main_layout.addLayout(content)

    def darken(self, hex_color):
        c = hex_color.lstrip('#')
        rgb = tuple(max(0, int(c[i:i+2], 16) - 40) for i in (0,2,4))
        return '#' + ''.join(f'{x:02x}' for x in rgb)

    def connect_db(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost", user="root", password="123456", database="inventory_system"
            )
            self.cursor = self.conn.cursor()
        except Exception as e:
            Toast(f"Lỗi kết nối CSDL: {e}", self, error=True).show()
            sys.exit(1)

    def load_data(self):
        self.table.setRowCount(0)
        self.cursor.execute("SELECT invoice, name, contact, `desc` FROM supplier")
        for row_data in self.cursor.fetchall():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, value in enumerate(row_data):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))

    def table_to_form(self, r, c):
        self.var_sup_invoice.setText(self.table.item(r, 0).text())
        self.var_name.setText(self.table.item(r, 1).text())
        self.var_contact.setText(self.table.item(r, 2).text())
        self.txt_desc.setPlainText(self.table.item(r, 3).text())

    def toast(self, msg): Toast(msg, self).show()
    def toast_error(self, msg): Toast(msg, self, error=True).show()

    def add(self):
        if not self.var_sup_invoice.text().strip():
            self.toast_error("Mã nhà cung cấp không được để trống!")
            return
        try:
            self.cursor.execute("SELECT 1 FROM supplier WHERE invoice=%s", (self.var_sup_invoice.text(),))
            if self.cursor.fetchone():
                self.toast_error("Mã nhà cung cấp đã tồn tại!")
                return
            self.cursor.execute(
                "INSERT INTO supplier(invoice, name, contact, `desc`) VALUES (%s,%s,%s,%s)",
                (self.var_sup_invoice.text(), self.var_name.text(), self.var_contact.text(), self.txt_desc.toPlainText())
            )
            self.conn.commit()
            self.toast("Thêm nhà cung cấp thành công!")
            self.clear()
            self.load_data()
        except Exception as e:
            self.toast_error(f"Lỗi: {e}")

    def update(self):
        if not self.var_sup_invoice.text().strip():
            self.toast_error("Chọn nhà cung cấp cần sửa!")
            return
        try:
            self.cursor.execute(
                "UPDATE supplier SET name=%s, contact=%s, `desc`=%s WHERE invoice=%s",
                (self.var_name.text(), self.var_contact.text(), self.txt_desc.toPlainText(), self.var_sup_invoice.text())
            )

            self.conn.commit()
            self.toast("Cập nhật thành công!")
            self.load_data()
        except Exception as e:
            self.toast_error(f"Lỗi: {e}")

    def delete_supplier(self):
        invoice = self.var_sup_invoice.text().strip()

        # Kiểm tra xem có chọn nhà cung cấp chưa
        if not invoice:
            QMessageBox.critical(self, "Lỗi", "Vui lòng chọn nhà cung cấp cần xóa!")
            return

        # Hiển thị hộp thoại xác nhận
        reply = QMessageBox.question(
            self,
            "Xác nhận",
            "Bạn có chắc muốn xóa nhà cung cấp này?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        # Nếu người dùng xác nhận xóa
        if reply == QMessageBox.Yes:
            try:
                self.cursor.execute("DELETE FROM supplier WHERE invoice=%s", (invoice,))
                self.conn.commit()

                QMessageBox.information(self, "Thành công", "✔ Xóa nhà cung cấp thành công!")
                self.clear()  # Reset form
                self.load_data()  # Load lại dữ liệu

            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Xảy ra lỗi khi xóa: {str(e)}")

    def clear(self):
        self.var_sup_invoice.clear()
        self.var_name.clear()
        self.var_contact.clear()
        self.txt_desc.clear()
        self.var_searchtxt.clear()
        self.load_data()

    def search(self):
        txt = self.var_searchtxt.text().strip()
        if not txt:
            self.toast_error("Nhập tên nhà cung cấp để tìm!")
            return

        try:
            self.cursor.execute("""
                                SELECT *
                                FROM supplier
                                WHERE name LIKE %s
                                """, (f"%{txt}%",))

            rows = self.cursor.fetchall() # trả về [()]
            self.table.setRowCount(0)

            if rows:
                for row_data in rows:
                    row = self.table.rowCount()
                    self.table.insertRow(row) # tăng row lên 1
                    for col, data in enumerate(row_data):
                        self.table.setItem(row, col, QTableWidgetItem(str(data)))
            else:
                self.toast_error("Không tìm thấy nhà cung cấp!")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))



if __name__ == "__main__":

    app = QApplication(sys.argv)
    win = SupplierWindow()
    win.show()
    sys.exit(app.exec())