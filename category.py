import os
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView
)

from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from create_db import get_connection  # Hàm tạo kết nối MySQL


class CategoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Management System | Category")
        self.setGeometry(320, 220, 1100, 500)
        self.var_cat_id = None

        # ---------- Layout chính ----------
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # ---------- Title ----------
        self.lbl_title = QLabel("Manage Product Category")
        self.lbl_title.setStyleSheet(
            "background-color:#184a45; color:white; font-size:30px; padding:10px;"
        )
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.lbl_title)

        # ---------- Input + Buttons ----------
        self.input_layout = QHBoxLayout()
        self.lbl_name = QLabel("Enter Category Name:")
        self.lbl_name.setStyleSheet("font-size:18px;")
        self.txt_name = QLineEdit()
        self.txt_name.setStyleSheet("background-color:lightyellow; font-size:18px;")

        self.btn_add = QPushButton("ADD")
        self.btn_add.setStyleSheet("background-color:#4caf50; color:white; font-size:15px;")
        self.btn_add.clicked.connect(self.add_category)

        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setStyleSheet("background-color:red; color:white; font-size:15px;")
        self.btn_delete.clicked.connect(self.delete_category)

        self.input_layout.addWidget(self.lbl_name)
        self.input_layout.addWidget(self.txt_name)
        self.input_layout.addWidget(self.btn_add)
        self.input_layout.addWidget(self.btn_delete)
        self.main_layout.addLayout(self.input_layout)

        # ---------- Table ----------
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["C ID", "Name"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.cellClicked.connect(self.get_data)
        self.main_layout.addWidget(self.table)

        # ---------- Images ----------
        self.img_layout = QHBoxLayout()
        self.im1 = QLabel()
        self.im1.setPixmap(
            QPixmap(r"D:\ALL_PROJECT\Python\Inventory-Management-System/images/cat.jpg").scaled(500, 250)
        )
        self.im2 = QLabel()
        self.im2.setPixmap(
            QPixmap(r"D:\ALL_PROJECT\Python\Inventory-Management-System/images/category.jpg").scaled(500, 250)
        )
        self.img_layout.addWidget(self.im1)
        self.img_layout.addWidget(self.im2)
        self.main_layout.addLayout(self.img_layout)

        # ---------- Load dữ liệu category ----------
        self.load_categories()

    # ---------- Thực thi query MySQL ----------
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
            QMessageBox.critical(self, "Database Error", f"Could not execute query:\n{e}")
            return [] if fetch else None

    # ---------- Load danh sách category ----------
    def load_categories(self):
        rows = self.execute_db("SELECT * FROM category", fetch=True)
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(row[0])))
            self.table.setItem(i, 1, QTableWidgetItem(row[1]))

    # ---------- Thêm category ----------
    def add_category(self):
        name = self.txt_name.text().strip()
        if not name:
            QMessageBox.critical(self, "Error", "Category Name must be required")
            return

        # Kiểm tra category đã tồn tại chưa
        rows = self.execute_db("SELECT * FROM category WHERE name=%s", (name,), fetch=True)
        if rows:
            QMessageBox.critical(self, "Error", "Category already present")
            return

        self.execute_db("INSERT INTO category(name) VALUES(%s)", (name,))
        QMessageBox.information(self, "Success", "Category Added Successfully")
        self.txt_name.clear()
        self.load_categories()

    # ---------- Lấy dữ liệu khi chọn table ----------
    def get_data(self, row, column):
        self.var_cat_id = self.table.item(row, 0).text()
        self.txt_name.setText(self.table.item(row, 1).text())

    # ---------- Xóa category ----------
    def delete_category(self):
        if not self.var_cat_id:
            QMessageBox.critical(self, "Error", "Select a category to delete")
            return

        reply = QMessageBox.question(
            self, "Confirm", "Do you really want to delete?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.execute_db("DELETE FROM category WHERE cid=%s", (self.var_cat_id,))
            QMessageBox.information(self, "Deleted", "Category Deleted Successfully")
            self.txt_name.clear()
            self.var_cat_id = None
            self.load_categories()


# ---------- RUN APP ----------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CategoryWindow()
    window.show()
    sys.exit(app.exec())  # exec() cho PySide6
