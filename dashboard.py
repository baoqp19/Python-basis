import sys
import os
import time
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QGridLayout, QFrame, QMessageBox, QStackedWidget
)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtGui import QFont, QPixmap, QColor, QPalette
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
        self.setGeometry(0, 0, 850, 500)
        # nền trắng, chữ đen, button xám
        QApplication.setStyle("Fusion")

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
        palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

        QApplication.setPalette(palette)

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
        # Thanh tiêu đề (title bar)
        title_widget = QWidget()
        title_widget.setStyleSheet("background-color: #010c48;")
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(20, 10, 20, 10)  # lề đẹp
        title_layout.setSpacing(15)

        # Logo bên trái
        logo = QLabel()
        pixmap = QPixmap(r"D:\ALL_PROJECT\Python\Inventory-Management-System\images\logo1.png")
        logo.setPixmap(pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setFixedSize(60, 60)
        title_layout.addWidget(logo)

        # Tiêu đề nằm chính giữa (dùng addStretch)
        title_label = QLabel("Inventory Management System")
        title_label.setFont(QFont("Times New Roman", 32, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignCenter)  # căn giữa chữ trong label

        title_layout.addStretch()  # đẩy logo sang trái
        title_layout.addWidget(title_label)  # chữ nằm giữa
        title_layout.addStretch()  # đẩy chữ vào giữa thật sự

        # Thêm vào layout chính
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
        for name in ["Dashboard", "Employee", "Supplier", "Category", "Products", "Sales","Billing", "Exit"]:
            btn = QPushButton(name)
            btn.setStyleSheet(btn_style)
            left_menu.addWidget(btn)
            self.menu_buttons[name] = btn

        body_layout.addWidget(menu_frame)

        self.stacked_widget = QStackedWidget()
        body_layout.addWidget(self.stacked_widget, stretch=1)

        # ===== TẠO CÁC MÀN HÌNH =====
        # Dashboard (biểu đồ tròn Matplotlib) – index 0
        self.dashboard_screen = self.create_modern_dashboard()
        self.stacked_widget.addWidget(self.dashboard_screen)

        # Employee – index 1
        self.employee_screen = EmployeeApp()
        self.stacked_widget.addWidget(self.employee_screen)

        # Supplier – index 2
        self.supplier_screen = SupplierWindow()
        self.stacked_widget.addWidget(self.supplier_screen)

        # Category – index 3
        self.category_screen = CategoryWindow()
        self.stacked_widget.addWidget(self.category_screen)

        # Products – index 4
        self.products_screen = ProductClass()
        self.stacked_widget.addWidget(self.products_screen)

        # Sales – index 5
        self.sales_screen = SalesClass()
        self.stacked_widget.addWidget(self.sales_screen)

        # Sales – index 6
        self.billing_screen = BillWindow()
        self.stacked_widget.addWidget(self.billing_screen)

        # ===== HIỂN THỊ DASHBOARD MẶC ĐỊNH =====
        self.stacked_widget.setCurrentIndex(0)  # hoặc setCurrentWidget(self.dashboard_screen)

        # ===== KẾT NỐI NÚT MENU TRÁI =====
        self.menu_buttons["Dashboard"].clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.menu_buttons["Employee"].clicked.connect(
            lambda: self.switch_to_screen(1, EmployeeApp)
        )

        self.menu_buttons["Supplier"].clicked.connect(
            lambda: self.switch_to_screen(2, SupplierWindow)
        )

        self.menu_buttons["Category"].clicked.connect(
            lambda: self.switch_to_screen(3, CategoryWindow)
        )

        self.menu_buttons["Products"].clicked.connect(
            lambda: self.switch_to_screen(4, ProductClass)
        )

        self.menu_buttons["Sales"].clicked.connect(
            lambda: self.switch_to_screen(5, SalesClass)
        )

        self.menu_buttons["Billing"].clicked.connect(
            lambda: self.switch_to_screen(6, BillWindow)
        )

        self.menu_buttons["Exit"].clicked.connect(self.close)

    def init_footer(self):
        footer = QLabel("Inventory Management System | Developed by BaoAndDuy\nContact: 818174556")
        footer.setAlignment(Qt.AlignCenter)
        footer.setFont(QFont("Times New Roman", 11))
        footer.setStyleSheet("background-color:#4d636d; color:white; padding:5px;")
        self.main_layout.addWidget(footer)

    def create_modern_dashboard(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)

        self.figure = Figure(figsize=(10, 8), facecolor="white")
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Vẽ lần đầu
        self.update_dashboard_charts()

        return widget

    def switch_to_screen(self, index, screen_class=None):

        old_widget = self.stacked_widget.widget(index)
        if old_widget:
            self.stacked_widget.removeWidget(old_widget)
            old_widget.deleteLater()

        # Tạo mới màn hình
        if screen_class:
            new_screen = screen_class()
            self.stacked_widget.insertWidget(index, new_screen)
            self.stacked_widget.setCurrentIndex(index)

    def update_dashboard_charts(self):
        try:

            con = get_connection()
            cur = con.cursor() # thực thi câu lệnh

            cur.execute("SELECT COUNT(*) FROM employee");
            emp = cur.fetchone()[0] # trả về tuple
            cur.execute("SELECT COUNT(*) FROM supplier");
            sup = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM category");
            cat = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM product");
            pro = cur.fetchone()[0]

            bill_path = r"D:\ALL_PROJECT\Python\Inventory-Management-System\bill"
            sales = len(os.listdir(bill_path)) if os.path.exists(bill_path) else 0
            values = [emp, sup, cat, pro, sales]
            con.close()


            labels = ['Nhân viên', 'Nhà cung cấp', 'Danh mục', 'Sản phẩm', 'Đơn bán hàng']
            colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']
            total = sum(values)

            self.figure.clear()

            # === BIỂU ĐỒ TRÒN BÊN TRÁI ===
            ax_pie = self.figure.add_axes([0.05, 0.1, 0.5, 0.8])
            wedges, texts, autotexts = ax_pie.pie(
                values,
                autopct=lambda pct: f"{pct:.1f}%" if pct >= 4 else "",
                colors=colors,
                startangle=90,
                wedgeprops=dict(width=0.4, edgecolor='white', linewidth=3), # tạo lỗ tròn ở giữa
                textprops=dict(color="white", fontsize=13, fontweight='bold'),
                pctdistance=0.75 # căn cho đẹp trong lỗ
            )

            # Tổng ở giữa
            if total > 0:
                ax_pie.text(0, 0, f"{total:,}\nTổng", ha='center', va='center',
                            fontsize=36, fontweight='bold', color='#2c3e50')
            ax_pie.set_aspect('equal')
            ax_pie.axis('off')

            # === BẢNG MÔ TẢ BÊN PHẢI ===
            ax_table = self.figure.add_axes([0.62, 0.2, 0.35, 0.6])
            ax_table.axis('off')

            # Tiêu đề bảng
            ax_table.text(0.5, 0.92, "CHI TIẾT THỐNG KÊ", ha='center', va='top',
                          fontsize=18, fontweight='bold', color='#2c3e50', transform=ax_table.transAxes)

            # Dữ liệu bảng
            cell_text = []
            for i, (label, val) in enumerate(zip(labels, values)):
                percent = (val / total * 100) if total > 0 else 0
                cell_text.append([label, f"{val:,}", f"{percent:.1f}%"])

            # Tạo bảng
            table = ax_table.table(
                cellText=cell_text,
                colLabels=['Danh mục', 'Số lượng', 'Tỷ lệ'],
                cellLoc='center',
                loc='center',
                bbox=[0, 0, 1, 0.8],
                colWidths=[0.5, 0.25, 0.25]
            )

            table.auto_set_font_size(False)
            table.set_fontsize(12)

            # Định dạng từng cell
            for i in range(len(labels)):
                for j in range(3):
                    cell = table[(i + 1, j)]
                    cell.set_height(0.12)
                    if j == 0:  # cột tên danh mục
                        cell.get_text().set_color('white')
                        cell.set_facecolor(colors[i])
                        cell.get_text().set_fontweight('bold')
                    else:
                        cell.set_facecolor('white')
                        if values[i] == 0:
                            cell.get_text().set_color('#999')
                        else:
                            cell.get_text().set_fontweight('bold')

            # Header bảng
            for j in range(3):
                table[(0, j)].set_facecolor('#34495e')
                table[(0, j)].get_text().set_color('white')
                table[(0, j)].get_text().set_fontweight('bold')

            # === TIÊU ĐỀ CHÍNH + THỜI GIAN ===
            self.figure.suptitle("TỔNG QUAN HỆ THỐNG", fontsize=28, fontweight='bold',
                                 color='#2c3e50', y=0.98)

            now = time.strftime("%d/%m/%Y - %H:%M:%S")
            self.figure.text(0.5, 0.02, f"Cập nhật lúc: {now}", ha='center',
                             fontsize=11, color='#7f8c8d')

            self.canvas.draw()

        except Exception as e:
            print(f"Lỗi biểu đồ: {e}")

    def update_content(self):
        try:
            current_time = time.strftime("%I:%M:%S %p")
            current_date = time.strftime("%d-%m-%Y")
            self.lbl_clock.setText(f"Welcome | Date: {current_date} | Time: {current_time}")

            # Chỉ gọi khi đã có hàm và canvas Matplotlib
            if hasattr(self, 'update_dashboard_charts'):
                self.update_dashboard_charts()

        except Exception as ex:
            print(f"Lỗi cập nhật dashboard: {ex}")

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
