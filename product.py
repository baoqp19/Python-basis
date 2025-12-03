import sys

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QGridLayout,
    QMessageBox, QHeaderView
)

from PySide6.QtCore import Qt
from create_db import get_connection

class ProductClass(QWidget):
    def __init__(self):
        super().__init__()

        # ===== Window Settings =====
        self.setStyleSheet("background-color: #f0f2f5;")

        # ===== Variables =====
        self.var_pid = ""
        self.cat_list = []
        self.sup_list = []
        self.fetch_cat_sup()

        # ===== Layout =====
        main_layout = QHBoxLayout(self)

        # -------- Left Panel: Form --------
        form_layout = QVBoxLayout()
        main_layout.addLayout(form_layout, 2)

        lbl_title = QLabel("Manage Product Details")
        lbl_title.setStyleSheet("background-color:#0f4d7d; color:white; font-size:18px; padding:5px;")
        lbl_title.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(lbl_title)

        grid = QGridLayout()
        form_layout.addLayout(grid)

        # Labels + Inputs
        grid.addWidget(QLabel("Category"), 0, 0)
        self.cmb_cat = QComboBox()
        self.cmb_cat.addItems(self.cat_list)
        grid.addWidget(self.cmb_cat, 0, 1)

        grid.addWidget(QLabel("Supplier"), 1, 0)
        self.cmb_sup = QComboBox()
        self.cmb_sup.addItems(self.sup_list)
        grid.addWidget(self.cmb_sup, 1, 1)

        grid.addWidget(QLabel("Name"), 2, 0)
        self.txt_name = QLineEdit()
        grid.addWidget(self.txt_name, 2, 1)

        grid.addWidget(QLabel("Price"), 3, 0)
        self.txt_price = QLineEdit()
        grid.addWidget(self.txt_price, 3, 1)

        grid.addWidget(QLabel("Quantity"), 4, 0)
        self.txt_qty = QLineEdit()
        grid.addWidget(self.txt_qty, 4, 1)

        grid.addWidget(QLabel("Status"), 5, 0)
        self.cmb_status = QComboBox()
        self.cmb_status.addItems(["Active", "Inactive"])
        grid.addWidget(self.cmb_status, 5, 1)

        # Buttons
        btn_layout = QHBoxLayout()
        form_layout.addLayout(btn_layout)
        btn_add = QPushButton("Save")
        btn_add.clicked.connect(self.add_product)
        btn_layout.addWidget(btn_add)
        btn_update = QPushButton("Update")
        btn_update.clicked.connect(self.update_product)
        btn_layout.addWidget(btn_update)
        btn_delete = QPushButton("Delete")
        btn_delete.clicked.connect(self.delete_product)
        btn_layout.addWidget(btn_delete)
        btn_clear = QPushButton("Clear")
        btn_clear.clicked.connect(self.clear_form)
        btn_layout.addWidget(btn_clear)

        # -------- Right Panel: Search + Table --------
        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout, 3)

        # Search
        search_layout = QHBoxLayout()
        right_layout.addLayout(search_layout)
        self.cmb_search = QComboBox()
        self.cmb_search.addItems(["Select", "Category", "Supplier", "Name"])
        search_layout.addWidget(self.cmb_search)
        self.txt_search = QLineEdit()
        search_layout.addWidget(self.txt_search)
        btn_search = QPushButton("Search")
        btn_search.clicked.connect(self.search_product)
        search_layout.addWidget(btn_search)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["PID", "Category", "Supplier", "Name", "Price", "Qty", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.cellClicked.connect(self.load_from_table)
        right_layout.addWidget(self.table)

        # Load data
        self.show_data()

    # -------- Database Methods --------
    def fetch_cat_sup(self):
        self.cat_list = ["Select"]
        self.sup_list = ["Select"]
        try:
            con = get_connection()
            cur = con.cursor()
            cur.execute("SELECT name FROM category")
            self.cat_list += [r[0] for r in cur.fetchall()]
            cur.execute("SELECT name FROM supplier")
            self.sup_list += [r[0] for r in cur.fetchall()]
            con.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def add_product(self):
        cat = self.cmb_cat.currentText()
        sup = self.cmb_sup.currentText()
        name = self.txt_name.text()
        price = self.txt_price.text()
        qty = self.txt_qty.text()
        status = self.cmb_status.currentText()
        if cat == "Select" or sup == "Select" or name == "":
            QMessageBox.warning(self, "Error", "All fields are required")
            return
        try:
            con = get_connection()
            cur = con.cursor()
            cur.execute("SELECT * FROM product WHERE name=%s", (name,))
            if cur.fetchone():
                QMessageBox.warning(self, "Error", "Product already exists")
            else:
                cur.execute("INSERT INTO product(Category,Supplier,name,price,qty,status) VALUES(%s,%s,%s,%s,%s,%s)",
                            (cat, sup, name, price, qty, status))
                con.commit()
                QMessageBox.information(self, "Success", "Product Added Successfully")
                self.clear_form()
                self.show_data()
            con.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def show_data(self):
        try:
            con = get_connection()
            cur = con.cursor()
            cur.execute("SELECT * FROM product")
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            con.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def load_from_table(self, row, col):
        self.var_pid = self.table.item(row, 0).text()
        self.cmb_cat.setCurrentText(self.table.item(row, 1).text())
        self.cmb_sup.setCurrentText(self.table.item(row, 2).text())
        self.txt_name.setText(self.table.item(row, 3).text())
        self.txt_price.setText(self.table.item(row, 4).text())
        self.txt_qty.setText(self.table.item(row, 5).text())
        self.cmb_status.setCurrentText(self.table.item(row, 6).text())

    def update_product(self):
        if self.var_pid == "":
            QMessageBox.warning(self, "Error", "Select a product to update")
            return
        try:
            con = get_connection()
            cur = con.cursor()
            cur.execute(
                "UPDATE product SET Category=%s,Supplier=%s,name=%s,price=%s,qty=%s,status=%s WHERE pid=%s",
                (self.cmb_cat.currentText(), self.cmb_sup.currentText(), self.txt_name.text(),
                 self.txt_price.text(), self.txt_qty.text(), self.cmb_status.currentText(), self.var_pid)
            )
            con.commit()
            QMessageBox.information(self, "Success", "Product Updated Successfully")
            self.clear_form()
            self.show_data()
            con.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_product(self):
        if self.var_pid == "":
            QMessageBox.warning(self, "Error", "Select a product to delete")
            return
        try:
            op = QMessageBox.question(self, "Confirm", "Do you really want to delete?",
                                      QMessageBox.Yes | QMessageBox.No)
            if op == QMessageBox.Yes:
                con = get_connection()
                cur = con.cursor()
                cur.execute("DELETE FROM product WHERE pid=%s", (self.var_pid,))
                con.commit()
                QMessageBox.information(self, "Success", "Product Deleted Successfully")
                self.clear_form()
                self.show_data()
                con.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def clear_form(self):
        self.var_pid = ""
        self.cmb_cat.setCurrentText("Select")
        self.cmb_sup.setCurrentText("Select")
        self.txt_name.clear()
        self.txt_price.clear()
        self.txt_qty.clear()
        self.cmb_status.setCurrentText("Active")
        self.cmb_search.setCurrentText("Select")
        self.txt_search.clear()
        self.show_data()

    def search_product(self):
        searchby = self.cmb_search.currentText()
        txt = self.txt_search.text()
        if searchby == "Select" or txt == "":
            QMessageBox.warning(self, "Error", "Select search option and input text")
            return
        try:
            con = get_connection()
            cur = con.cursor()
            query = f"SELECT * FROM product WHERE {searchby} LIKE %s"
            cur.execute(query, (f"%{txt}%",))
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            con.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductClass()
    window.show()
    sys.exit(app.exec())
