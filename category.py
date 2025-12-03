from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QFrame
)
from PySide6.QtGui import QPixmap, QFont, QIcon
from PySide6.QtCore import Qt
import os
import sys
from create_db import get_connection

class CategoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản Lý Danh Mục Sản Phẩm")
        self.setGeometry(200, 100, 1200, 700)
        self.var_cat_id = None

        # ===== MAIN LAYOUT =====
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # ===== TIÊU ĐỀ ĐẸP =====
        title = QLabel("QUẢN LÝ DANH MỤC SẢN PHẨM")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet("""
            QLabel {
                color: #1e40af;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #1e40af);
                color: white;
                padding: 20px;
                border-radius: 16px;
            }
        """)
        main_layout.addWidget(title)

        # ===== FORM NHẬP + NÚT =====
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)
        form_layout = QHBoxLayout(form_frame)
        form_layout.setContentsMargins(25, 25, 25, 25)
        form_layout.setSpacing(15)

        lbl_name = QLabel("Tên danh mục")
        lbl_name.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl_name.setStyleSheet("color: #0f172a;")

        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Nhập tên danh mục mới...")
        self.txt_name.setFixedHeight(50)
        self.txt_name.setStyleSheet("""
            QLineEdit {
                border: 2px solid #cbd5e1;
                border-radius: 12px;
                padding: 0 16px;
                font-size: 15px;
                background: white;
                color: black;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
            }
        """)

        self.btn_add = QPushButton("Thêm Mới")
        self.btn_add.setFixedHeight(50)
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #10b981, stop:1 #059669);
                color: white;
                font-weight: bold;
                font-size: 15px;
                border-radius: 12px;
                padding: 0 30px;
            }
            QPushButton:hover { background: #059669; }
            QPushButton:pressed { background: #047857; }
        """)
        self.btn_add.clicked.connect(self.add_category)

        self.btn_delete = QPushButton("Xóa")
        self.btn_delete.setFixedHeight(50)
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ef4444, stop:1 #dc2626);
                color: white;
                font-weight: bold;
                font-size: 15px;
                border-radius: 12px;
                padding: 0 30px;
            }
            QPushButton:hover { background: #dc2626; }
        """)
        self.btn_delete.clicked.connect(self.delete_category)

        form_layout.addWidget(lbl_name)
        form_layout.addWidget(self.txt_name, stretch=1)
        form_layout.addWidget(self.btn_add)
        form_layout.addWidget(self.btn_delete)

        main_layout.addWidget(form_frame)

        # ===== BẢNG DỮ LIỆU ĐẸP =====
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Mã DM", "Tên Danh Mục"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setStyleSheet("""
            QHeaderView::section {
                background: #1e40af;
                color: white;
                padding: 12px;
                font-weight: bold;
                border: none;
            }
        """)

        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                gridline-color: #e2e8f0;
                background: white;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 12px;
                color: black;
            }
            QTableWidget::item:selected {
                background: #dbeafe;
                color: #1e40af;
            }
        """)
        self.table.cellClicked.connect(self.get_data)
        main_layout.addWidget(self.table, stretch=1)

        # ===== HÌNH ẢNH (tùy chọn, giữ lại nhưng nhỏ hơn) =====
        img_layout = QHBoxLayout()
        img_layout.setSpacing(20)

        im1 = QLabel()
        im1.setPixmap(QPixmap("images/cat.jpg").scaled(250, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        im1.setAlignment(Qt.AlignCenter)
        im1.setStyleSheet("background: white; border-radius: 12px; padding: 10px; border: 1px solid #e2e8f0;")

        im2 = QLabel()
        im2.setPixmap(QPixmap("images/category.jpg").scaled(250, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        im2.setAlignment(Qt.AlignCenter)
        im2.setStyleSheet("background: white; border-radius: 12px; padding: 10px; border: 1px solid #e2e8f0;")

        img_layout.addWidget(im1)
        img_layout.addWidget(im2)
        main_layout.addLayout(img_layout)

        # Load dữ liệu
        self.load_categories()

    # Giữ nguyên các hàm execute_db, load_categories, add_category, get_data, delete_category
    # (copy y nguyên từ code cũ của bạn vào đây là được)

    def execute_db(self, query, params=(), fetch=False):
        try:
            con = get_connection()
            cur = con.cursor()
            cur.execute(query, params)
            if fetch:
                result = cur.fetchall()
            else:
                con.commit()
                result = None
            con.close()
            return result
        except Exception as e:
            QMessageBox.critical(self, "Lỗi CSDL", f"Không thể thực hiện:\n{e}")
            return [] if fetch else None

    def load_categories(self):
        rows = self.execute_db("SELECT * FROM category", fetch=True)
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(row[0])))
            self.table.setItem(i, 1, QTableWidgetItem(row[1]))

    def add_category(self):
        name = self.txt_name.text().strip()
        if not name:
            QMessageBox.critical(self, "Lỗi", "Vui lòng nhập tên danh mục!")
            return
        if self.execute_db("SELECT * FROM category WHERE name=%s", (name,), fetch=True):
            QMessageBox.critical(self, "Lỗi", "Danh mục đã tồn tại!")
            return
        self.execute_db("INSERT INTO category(name) VALUES(%s)", (name,))
        QMessageBox.information(self, "Thành công", "Thêm danh mục thành công!")
        self.txt_name.clear()
        self.load_categories()

    def get_data(self, row, column):
        self.var_cat_id = self.table.item(row, 0).text()
        self.txt_name.setText(self.table.item(row, 1).text())

    def delete_category(self):
        if not self.var_cat_id:
            QMessageBox.critical(self, "Lỗi", "Vui lòng chọn danh mục cần xóa!")
            return
        reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa danh mục này?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.execute_db("DELETE FROM category WHERE cid=%s", (self.var_cat_id,))
            QMessageBox.information(self, "Thành công", "Xóa thành công!")
            self.txt_name.clear()
            self.var_cat_id = None
            self.load_categories()

# ---------- RUN APP ----------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CategoryWindow()
    window.show()
    sys.exit(app.exec())  # exec() cho PySide6
