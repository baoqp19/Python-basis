import sys
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QListWidget,
    QTextEdit, QVBoxLayout, QHBoxLayout, QFrame, QScrollBar, QMessageBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class SalesClass(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Management System | Nishant Gupta")
        self.setGeometry(320,220,1100,500)
        self.setFixedSize(1100,500)
        self.blll_list = []

        self.var_invoice = ""

        # ===== Title =====
        lbl_title = QLabel("View Customer Bills")
        lbl_title.setStyleSheet("background-color:#184a45; color:white; font-size:30px; padding:10px;")
        lbl_title.setAlignment(Qt.AlignCenter)

        # ===== Search Area =====
        lbl_invoice = QLabel("Invoice No.")
        self.txt_invoice = QLineEdit()
        btn_search = QPushButton("Search")
        btn_search.clicked.connect(self.search)
        btn_clear = QPushButton("Clear")
        btn_clear.clicked.connect(self.clear)

        search_layout = QHBoxLayout()
        search_layout.addWidget(lbl_invoice)
        search_layout.addWidget(self.txt_invoice)
        search_layout.addWidget(btn_search)
        search_layout.addWidget(btn_clear)

        # ===== Bill List =====
        self.sales_list = QListWidget()
        self.sales_list.itemClicked.connect(self.get_data)

        # ===== Bill Area =====
        self.bill_area = QTextEdit()
        self.bill_area.setReadOnly(True)

        # ===== Image =====
        self.lbl_image = QLabel()
        pixmap = QPixmap(r"D:\ALL_PROJECT\Python\Inventory-Management-System/images/cat2.jpg")
        pixmap = pixmap.scaled(450,300,Qt.KeepAspectRatio,Qt.SmoothTransformation)
        self.lbl_image.setPixmap(pixmap)

        # ===== Layouts =====
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.sales_list)

        middle_layout = QVBoxLayout()
        middle_layout.addWidget(self.bill_area)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.lbl_image)

        bottom_layout = QHBoxLayout()
        bottom_layout.addLayout(left_layout)
        bottom_layout.addLayout(middle_layout)
        bottom_layout.addLayout(right_layout)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(lbl_title)
        main_layout.addLayout(search_layout)
        main_layout.addLayout(bottom_layout)

        self.show_bills()

    # ---------------- Functions ----------------
    def show_bills(self):
        self.blll_list.clear()
        self.sales_list.clear()
        path = r"D:\ALL_PROJECT\Python\Inventory-Management-System/bill"
        if os.path.exists(path):
            for i in os.listdir(path):
                if i.endswith('.txt'):
                    self.sales_list.addItem(i)
                    self.blll_list.append(i.split('.')[0])

    def get_data(self,item):
        file_name = item.text()
        self.bill_area.clear()
        try:
            with open(rf"D:\ALL_PROJECT\Python\Inventory-Management-System\bill\{file_name}", "r") as fp:
                self.bill_area.setPlainText(fp.read())
        except Exception as ex:
            QMessageBox.critical(self,"Error",str(ex))

    def search(self):
        invoice = self.txt_invoice.text()
        if invoice=="":
            QMessageBox.warning(self,"Error","Invoice no. should be required")
            return
        if invoice in self.blll_list:
            try:
                with open(rf"D:\ALL_PROJECT\Python\Inventory-Management-System\bill\{invoice}.txt","r") as fp:
                    self.bill_area.setPlainText(fp.read())
            except Exception as ex:
                QMessageBox.critical(self,"Error",str(ex))
        else:
            QMessageBox.warning(self,"Error","Invalid Invoice No.")

    def clear(self):
        self.txt_invoice.clear()
        self.bill_area.clear()
        self.show_bills()

if __name__=="__main__":
    app = QApplication(sys.argv)
    window = SalesClass()
    window.show()
    sys.exit(app.exec())
