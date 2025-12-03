import sys
import os
import time
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QGridLayout, QFrame, QMessageBox, QStackedWidget
)
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtCore import Qt, QTimer
from create_db import create_db, get_connection
from employee import EmployeeApp
from category import CategoryWindow
from supplier import SupplierWindow
from billing import BillWindow
from sales import SalesClass
from product import ProductClass
# Tạo DB nếu chưa có
create_db()

class IMS(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Management System")
        self.setGeometry(200, 100, 1350, 700)
        self.setStyleSheet("background-color: white;")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.init_title()
        self.init_clock()
        self.init_body()
        self.init_footer()

        # Update đồng hồ và dữ liệu dashboard
        self.update_content()
        timer = QTimer(self)
        timer.timeout.connect(self.update_content)
        timer.start(1000)

    def init_title(self):
        title_widget = QWidget()
        title_widget.setStyleSheet("background-color: #010c48;")
        title_layout = QHBoxLayout(title_widget)

        logo = QLabel()
        logo.setPixmap(QPixmap(r"D:\ALL_PROJECT\Python\Inventory-Management-System\images\logo1.png").scaled(60, 60))
        title_label = QLabel("Inventory Management System")
        title_label.setFont(QFont("Times New Roman", 32, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        title_layout.addWidget(logo)
        title_layout.addWidget(title_label)

        self.main_layout.addWidget(title_widget)

    def init_clock(self):
        self.lbl_clock = QLabel("Welcome | Date: -- | Time: --")
        self.lbl_clock.setFont(QFont("Times New Roman", 14))
        self.lbl_clock.setStyleSheet("background-color:#4d636d; color:white; padding:6px;")
        self.main_layout.addWidget(self.lbl_clock)

    def init_body(self):
        body_layout = QHBoxLayout()
        self.main_layout.addLayout(body_layout)

        # ---------- Left Menu ----------
        left_menu = QVBoxLayout()
        menu_frame = QFrame()
        menu_frame.setLayout(left_menu)
        menu_frame.setFixedWidth(220)
        menu_frame.setStyleSheet("background-color:white; border:1px solid #ccc;")

        logo_menu = QLabel()
        logo_menu.setPixmap(QPixmap(r"D:\ALL_PROJECT\Python\Inventory-Management-System\images\menu_im.png").scaled(180, 180))
        logo_menu.setAlignment(Qt.AlignCenter)
        left_menu.addWidget(logo_menu)

        lbl_menu = QLabel("Menu")
        lbl_menu.setFont(QFont("Times New Roman", 20, QFont.Bold))
        lbl_menu.setStyleSheet("background-color:#009688; color:white; padding:8px;")
        lbl_menu.setAlignment(Qt.AlignCenter)
        left_menu.addWidget(lbl_menu)

        btn_style = """
        QPushButton {
            background-color: #ffffff;
            border: 1px solid #ccc;
            color: #333333;
            font-weight: bold;
            text-align: center;
            padding: 10px;
            font-size: 16px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #009688;
            color: #ffffff;
        }
        QPushButton:pressed {
            background-color: #00796b;
            color: #ffffff;
        }
        """

        # ---------- Tạo các button menu ----------
        self.menu_buttons = {}
        for name in ["Dashboard", "Employee", "Supplier", "Category", "Products", "Sales", "Exit"]:
            btn = QPushButton(name)
            btn.setStyleSheet(btn_style)
            left_menu.addWidget(btn)
            self.menu_buttons[name] = btn

        body_layout.addWidget(menu_frame)

        # ---------- Stacked Widget cho body ----------
        self.stacked_widget = QStackedWidget()
        body_layout.addWidget(self.stacked_widget)

        # ----- Dashboard Screen -----
        self.dashboard_screen = QWidget()
        dashboard_layout = QGridLayout()
        self.dashboard_screen.setLayout(dashboard_layout)

        # ----- Employee Screen -----
        self.employee_screen = EmployeeApp()
        self.stacked_widget.addWidget(self.employee_screen)

        self.menu_buttons["Employee"].clicked.connect(
            lambda: self.stacked_widget.setCurrentWidget(self.employee_screen)
        )

        # ----- Supplier Screen -----
        self.supplier_screen = SupplierWindow()
        self.stacked_widget.addWidget(self.supplier_screen)

        self.menu_buttons["Supplier"].clicked.connect(
            lambda: self.stacked_widget.setCurrentWidget(self.supplier_screen)
        )

        # ----- Category Screen -----
        self.category_screen = CategoryWindow()
        self.stacked_widget.addWidget(self.category_screen)

        self.menu_buttons["Category"].clicked.connect(
            lambda: self.stacked_widget.setCurrentWidget(self.category_screen)
        )

        # ----- Products Screen -----
        self.products_screen = ProductClass()
        self.stacked_widget.addWidget(self.products_screen)

        self.menu_buttons["Products"].clicked.connect(
            lambda: self.stacked_widget.setCurrentWidget(self.products_screen)
        )

        # ----- Sales Screen -----
        self.sales_screen = SalesClass()
        self.stacked_widget.addWidget(self.sales_screen)

        self.menu_buttons["Sales"].clicked.connect(
            lambda: self.stacked_widget.setCurrentWidget(self.sales_screen)
        )

        def stat_card(text, color):
            lbl = QLabel(text)
            lbl.setFont(QFont("Goudy Old Style", 18, QFont.Bold))
            lbl.setStyleSheet(f"background-color:{color}; color:white; border-radius:10px;")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFixedSize(300, 150)
            return lbl

        self.lbl_employee = stat_card("Total Employee\n[ 0 ]", "#33bbf9")
        self.lbl_supplier = stat_card("Total Supplier\n[ 0 ]", "#ff5722")
        self.lbl_category = stat_card("Total Category\n[ 0 ]", "#009688")
        self.lbl_product = stat_card("Total Product\n[ 0 ]", "#607d8b")
        self.lbl_sales = stat_card("Total Sales\n[ 0 ]", "#ffc107")

        dashboard_layout.addWidget(self.lbl_employee, 0, 0)
        dashboard_layout.addWidget(self.lbl_supplier, 0, 1)
        dashboard_layout.addWidget(self.lbl_category, 0, 2)
        dashboard_layout.addWidget(self.lbl_product, 1, 0)
        dashboard_layout.addWidget(self.lbl_sales, 1, 1)
        dashboard_layout.setAlignment(Qt.AlignTop)

        self.stacked_widget.addWidget(self.dashboard_screen)  # index 0

        # ----- Employee Screen -----
        self.employee_screen = EmployeeApp()
        self.stacked_widget.addWidget(self.employee_screen)  # index 1

        # Hiển thị dashboard mặc định
        self.stacked_widget.setCurrentWidget(self.dashboard_screen)

        # ----- Nối sự kiện nút menu -----
        self.menu_buttons["Dashboard"].clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.dashboard_screen))
        self.menu_buttons["Employee"].clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.employee_screen))
        self.menu_buttons["Exit"].clicked.connect(self.close)

    def init_footer(self):
        footer = QLabel("Inventory Management System | Developed by BaoAndDuy\nContact: 818174556")
        footer.setAlignment(Qt.AlignCenter)
        footer.setFont(QFont("Times New Roman", 11))
        footer.setStyleSheet("background-color:#4d636d; color:white; padding:5px;")
        self.main_layout.addWidget(footer)

    def update_content(self):
        try:
            con = get_connection()
            cur = con.cursor()

            cur.execute("SELECT COUNT(*) FROM product")
            self.lbl_product.setText(f"Total Product\n[ {cur.fetchone()[0]} ]")

            cur.execute("SELECT COUNT(*) FROM category")
            self.lbl_category.setText(f"Total Category\n[ {cur.fetchone()[0]} ]")

            cur.execute("SELECT COUNT(*) FROM employee")
            self.lbl_employee.setText(f"Total Employee\n[ {cur.fetchone()[0]} ]")

            cur.execute("SELECT COUNT(*) FROM supplier")
            self.lbl_supplier.setText(f"Total Supplier\n[ {cur.fetchone()[0]} ]")

            bill_count = len(os.listdir(r"D:\ALL_PROJECT\Python\Inventory-Management-System\bill"))
            self.lbl_sales.setText(f"Total Sales\n[ {bill_count} ]")

            # Update thời gian
            time_ = time.strftime("%I:%M:%S %p")
            date_ = time.strftime("%d-%m-%Y")
            self.lbl_clock.setText(f"Welcome | Date: {date_} | Time: {time_}")

            con.close()
        except Exception as ex:
            QMessageBox.critical(self, "Error", f"Error: {ex}")

# ----------- RUN APP ------------
if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = IMS()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        import traceback
        traceback.print_exc()
