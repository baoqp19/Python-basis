import sys, time, os, tempfile
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit, QTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout, QHBoxLayout,
    QFrame, QMessageBox, QGridLayout, QSpinBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap
from create_db import get_connection

class BillWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Management System | Nishant Gupta")
        self.setGeometry(100, 50, 1350, 700)

        # State variables
        self.cart_list = []
        self.chk_print = 0
        self.var_cname = ""
        self.var_contact = ""

        # Layout chính
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        # ===== Title + Logout =====
        title_layout = QHBoxLayout()
        self.icon_title = QLabel()
        pixmap = QPixmap(r"D:\ALL_PROJECT\Python\Inventory-Management-System\images\logo1.png")
        self.icon_title.setPixmap(pixmap.scaled(60,60,Qt.KeepAspectRatio))
        title_label = QLabel("Inventory Management System")
        title_label.setStyleSheet("background-color:#010c48; color:white; font-size:30px; padding:10px;")
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        btn_logout = QPushButton("Logout")
        btn_logout.setStyleSheet("background-color:yellow; font-size:15px;")
        btn_logout.setFixedSize(150,50)
        title_layout.addWidget(self.icon_title)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(btn_logout)
        main_layout.addLayout(title_layout)

        # ===== Clock =====
        self.lbl_clock = QLabel()
        self.lbl_clock.setStyleSheet("background-color:#4d636d; color:white; font-size:15px; padding:5px;")
        self.lbl_clock.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.lbl_clock)
        self.update_date_time()

        # ===== Body Layout =====
        body_layout = QHBoxLayout()
        main_layout.addLayout(body_layout)

        # ===== Left Panel: Products =====
        left_panel = QVBoxLayout()
        body_layout.addLayout(left_panel, 3)

        lbl_products = QLabel("All Products")
        lbl_products.setStyleSheet("background-color:#262626; color:white; font-size:20px; padding:5px;")
        lbl_products.setAlignment(Qt.AlignCenter)
        left_panel.addWidget(lbl_products)

        # Search
        search_layout = QHBoxLayout()
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Enter product name...")
        btn_search = QPushButton("Search")
        btn_search.clicked.connect(self.search_product)
        btn_show_all = QPushButton("Show All")
        btn_show_all.clicked.connect(self.show_products)
        search_layout.addWidget(self.txt_search)
        search_layout.addWidget(btn_search)
        search_layout.addWidget(btn_show_all)
        left_panel.addLayout(search_layout)

        # Product Table
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(5)
        self.product_table.setHorizontalHeaderLabels(["PID","Name","Price","Qty","Status"])
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.product_table.cellClicked.connect(self.select_product)
        left_panel.addWidget(self.product_table)
        self.show_products()

        # ===== Middle Panel: Customer + Cart =====
        middle_panel = QVBoxLayout()
        body_layout.addLayout(middle_panel, 4)

        # Customer Info
        customer_frame = QHBoxLayout()
        self.txt_cname = QLineEdit()
        self.txt_cname.setPlaceholderText("Customer Name")
        self.txt_contact = QLineEdit()
        self.txt_contact.setPlaceholderText("Contact")
        customer_frame.addWidget(QLabel("Customer Name:"))
        customer_frame.addWidget(self.txt_cname)
        customer_frame.addWidget(QLabel("Contact:"))
        customer_frame.addWidget(self.txt_contact)
        middle_panel.addLayout(customer_frame)

        # Cart Table
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(4)
        self.cart_table.setHorizontalHeaderLabels(["PID","Name","Price","Qty"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cart_table.cellClicked.connect(self.select_cart_item)
        middle_panel.addWidget(self.cart_table)

        # Add to Cart controls
        add_layout = QHBoxLayout()
        self.txt_pid = QLineEdit()
        self.txt_pid.setReadOnly(True)
        self.txt_pname = QLineEdit()
        self.txt_pname.setReadOnly(True)
        self.txt_price = QLineEdit()
        self.txt_price.setReadOnly(True)
        self.spin_qty = QSpinBox()
        self.spin_qty.setMinimum(1)
        btn_add_cart = QPushButton("Add/Update Cart")
        btn_add_cart.clicked.connect(self.add_update_cart)
        add_layout.addWidget(QLabel("PID:"))
        add_layout.addWidget(self.txt_pid)
        add_layout.addWidget(QLabel("Name:"))
        add_layout.addWidget(self.txt_pname)
        add_layout.addWidget(QLabel("Price:"))
        add_layout.addWidget(self.txt_price)
        add_layout.addWidget(QLabel("Qty:"))
        add_layout.addWidget(self.spin_qty)
        add_layout.addWidget(btn_add_cart)
        middle_panel.addLayout(add_layout)

        # ===== Right Panel: Bill Area =====
        right_panel = QVBoxLayout()
        body_layout.addLayout(right_panel, 3)

        lbl_bill = QLabel("Customer Bill Area")
        lbl_bill.setStyleSheet("background-color:#262626; color:white; font-size:20px; padding:5px;")
        lbl_bill.setAlignment(Qt.AlignCenter)
        right_panel.addWidget(lbl_bill)

        self.txt_bill_area = QTextEdit()
        right_panel.addWidget(self.txt_bill_area)

        # Bill buttons
        btn_layout = QHBoxLayout()
        btn_generate = QPushButton("Generate Bill")
        btn_generate.clicked.connect(self.generate_bill)
        btn_print = QPushButton("Print")
        btn_print.clicked.connect(self.print_bill)
        btn_clear_all = QPushButton("Clear All")
        btn_clear_all.clicked.connect(self.clear_all)
        btn_layout.addWidget(btn_generate)
        btn_layout.addWidget(btn_print)
        btn_layout.addWidget(btn_clear_all)
        right_panel.addLayout(btn_layout)

    # ================= Functions =================
    def update_date_time(self):
        now = time.strftime("%d-%m-%Y %H:%M:%S")
        self.lbl_clock.setText(f"Welcome to IMS\t\t {now}")
        QTimer.singleShot(1000, self.update_date_time)

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
            QMessageBox.critical(self, "Database Error", str(e))
            return [] if fetch else None

    def show_products(self):
        rows = self.execute_db("SELECT pid,name,price,qty,status FROM product WHERE status='Active'", fetch=True)
        self.product_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.product_table.setItem(i,j,QTableWidgetItem(str(val)))

    def search_product(self):
        term = self.txt_search.text()
        if not term:
            QMessageBox.warning(self, "Error", "Search input required")
            return
        rows = self.execute_db("SELECT pid,name,price,qty,status FROM product WHERE name LIKE %s", 
                               ('%'+term+'%',), fetch=True)
        self.product_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.product_table.setItem(i,j,QTableWidgetItem(str(val)))

    def select_product(self, row, column):
        self.txt_pid.setText(self.product_table.item(row,0).text())
        self.txt_pname.setText(self.product_table.item(row,1).text())
        self.txt_price.setText(self.product_table.item(row,2).text())
        self.spin_qty.setValue(int(self.product_table.item(row,3).text()))

    def select_cart_item(self, row, column):
        self.txt_pid.setText(self.cart_table.item(row,0).text())
        self.txt_pname.setText(self.cart_table.item(row,1).text())
        self.txt_price.setText(self.cart_table.item(row,2).text())
        self.spin_qty.setValue(int(self.cart_table.item(row,3).text()))

    def add_update_cart(self):
        pid = self.txt_pid.text()
        name = self.txt_pname.text()
        price = self.txt_price.text()
        qty = self.spin_qty.value()
        if not pid:
            QMessageBox.warning(self, "Error", "Select a product")
            return
        # Update cart list
        found = False
        for i, item in enumerate(self.cart_list):
            if item[0]==pid:
                self.cart_list[i] = [pid,name,price,qty]
                found = True
                break
        if not found:
            self.cart_list.append([pid,name,price,qty])
        self.show_cart()

    def show_cart(self):
        self.cart_table.setRowCount(len(self.cart_list))
        for i,row in enumerate(self.cart_list):
            for j,val in enumerate(row):
                self.cart_table.setItem(i,j,QTableWidgetItem(str(val)))

    def generate_bill(self):
        if not self.cart_list:
            QMessageBox.warning(self,"Error","Cart is empty")
            return
        self.txt_bill_area.clear()
        total = 0
        self.txt_bill_area.append("XYZ-Inventory\nPhone: 9899459288\n"+"="*40)
        for row in self.cart_list:
            name = row[1]; qty=int(row[3]); price=float(row[2])
            self.txt_bill_area.append(f"{name}\t{qty}\tRs.{price*qty}")
            total += price*qty
            # Update DB qty
            db_qty = self.execute_db("SELECT qty FROM product WHERE pid=%s",(row[0],),fetch=True)[0][0]
            new_qty = db_qty - qty
            status = "Inactive" if new_qty==0 else "Active"
            self.execute_db("UPDATE product SET qty=%s,status=%s WHERE pid=%s",(new_qty,status,row[0]))
        discount = total*0.05
        net = total - discount
        self.txt_bill_area.append("="*40)
        self.txt_bill_area.append(f"Total: Rs.{total}")
        self.txt_bill_area.append(f"Discount 5%: Rs.{discount}")
        self.txt_bill_area.append(f"Net Pay: Rs.{net}")
        self.show_products()

    def print_bill(self):
        if self.cart_list:
            file_path = tempfile.mktemp(".txt")
            with open(file_path,'w') as f:
                f.write(self.txt_bill_area.toPlainText())
            os.startfile(file_path,'print')
        else:
            QMessageBox.information(self,"Info","Generate bill first")

    def clear_all(self):
        self.cart_list.clear()
        self.show_cart()
        self.txt_bill_area.clear()
        self.txt_pid.clear()
        self.txt_pname.clear()
        self.txt_price.clear()
        self.spin_qty.setValue(1)
        self.txt_cname.clear()
        self.txt_contact.clear()
        self.show_products()


if __name__=="__main__":
    app = QApplication(sys.argv)
    window = BillWindow()
    window.show()
    sys.exit(app.exec())
