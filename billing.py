# bill.py - Giao diện hóa đơn bán hàng SIÊU ĐẸP bằng PySide6
import sys, os, time, tempfile
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit, QTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout, QHBoxLayout,
    QGridLayout,
    QFrame, QMessageBox, QSpinBox, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap, QIcon, QColor
from create_db import get_connection


class BillWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.cart_list = []
        self.setWindowTitle("Hóa Đơn Bán Hàng - Inventory Management System")
        self.setGeometry(100, 50, 1400, 780)
        self.setStyleSheet("background-color: #f4f6f9;")

        self.init_ui()
        self.start_clock()
        self.load_products()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ===================== HEADER =====================
        header = QWidget()
        header.setFixedHeight(90)
        header.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #0d6efd, stop:1 #6610f2);
            border-bottom: 3px solid #ffd700;
        """)
        hbox = QHBoxLayout(header)
        hbox.setContentsMargins(25, 10, 25, 10)

        # Logo
        logo = QLabel()
        logo.setPixmap(QPixmap(r"images/logo1.png").scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        hbox.addWidget(logo)

        # Tiêu đề
        title = QLabel("INVENTORY MANAGEMENT SYSTEM")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setStyleSheet("color: white;")
        hbox.addWidget(title)
        hbox.addStretch()

        # Nút Logout
        btn_logout = QPushButton("Đăng xuất")
        btn_logout.setFixedSize(140, 50)
        btn_logout.setStyleSheet("""
            QPushButton {
                background: #ff4757; color: white; font-weight: bold;
                border-radius: 25px; font-size: 16px;
            }
            QPushButton:hover { background: #ff3742; }
        """)
        hbox.addWidget(btn_logout)

        main_layout.addWidget(header)

        # ===================== CLOCK =====================
        self.lbl_clock = QLabel()
        self.lbl_clock.setFixedHeight(40)
        self.lbl_clock.setFont(QFont("Consolas", 14))
        self.lbl_clock.setStyleSheet("""
            background: #2c3e50; color: #00ff88; 
            padding: 8px; border-bottom: 2px solid #34495e;
        """)
        self.lbl_clock.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.lbl_clock)

        # ===================== BODY =====================
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(20, 20, 20, 20)
        body_layout.setSpacing(20)
        main_layout.addWidget(body, 1)

        # ------------------ CỘT TRÁI: SẢN PHẨM ------------------
        left = QFrame()
        left.setStyleSheet("""
            background: white; border-radius: 15px;
            border: 1px solid #e0e0e0; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        """)
        left_layout = QVBoxLayout(left)

        # Tiêu đề danh sách sản phẩm (SỬA CHỖ NÀY)
        title_left = QLabel("DANH SÁCH SẢN PHẨM")
        title_left.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_left.setStyleSheet("background:#2c3e50; color:white; padding:15px; border-radius:12px 12px 0 0;")
        title_left.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title_left)

        # Thanh tìm kiếm đẹp
        search_bar = QWidget()
        search_bar.setStyleSheet("background:#f8f9fa; border-radius:10px; padding:10px;")
        sbox = QHBoxLayout(search_bar)
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Tìm kiếm sản phẩm...")
        self.txt_search.setStyleSheet("""
            padding: 12px; border: 2px solid #ddd; border-radius: 10px;
            font-size: 14px;
        """)
        btn_search = QPushButton("Tìm")
        btn_search.clicked.connect(self.search_product)
        btn_search.setStyleSheet("background:#4361ee; color:white; padding:12px 20px; border-radius:8px; font-weight:bold;")
        btn_show = QPushButton("Tất cả")
        btn_show.clicked.connect(self.load_products)
        btn_show.setStyleSheet("background:#7209b7; color:white; padding:12px 20px; border-radius:8px; font-weight:bold;")
        sbox.addWidget(self.txt_search)
        sbox.addWidget(btn_search)
        sbox.addWidget(btn_show)
        left_layout.addWidget(search_bar)

        # Bảng sản phẩm
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(5)
        self.product_table.setHorizontalHeaderLabels(["Mã SP", "Tên sản phẩm", "Giá", "Tồn kho", "Trạng thái"])
        header = self.product_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.product_table.setStyleSheet("""
            QTableWidget { 
                gridline-color: #ddd; font-size: 13px; 
                alternate-background-color: #f8f9fa;
            }
            QHeaderView::section { background: #4361ee; color: white; padding: 10px; }
        """)
        self.product_table.setAlternatingRowColors(True)
        self.product_table.cellClicked.connect(self.select_product)
        left_layout.addWidget(self.product_table)

        body_layout.addWidget(left, 3)

        # ------------------ CỘT GIỮA: KHÁCH HÀNG + GIỎ HÀNG ------------------
        center = QFrame()
        center.setStyleSheet("background: white; border-radius: 15px; border: 1px solid #e0e0e0;")
        cvbox = QVBoxLayout(center)
        cvbox.setSpacing(15)

        # Thông tin khách hàng
        cust_frame = QFrame()
        cust_frame.setStyleSheet("background:#e8f5e8; border-radius:12px; padding:15px;")
        cgrid = QGridLayout(cust_frame)
        cgrid.addWidget(QLabel("Tên khách hàng:"), 0, 0)
        self.txt_cname = QLineEdit()
        self.txt_cname.setStyleSheet("padding:10px; border-radius:8px; border:1px solid #ccc;")
        cgrid.addWidget(self.txt_cname, 0, 1)
        cgrid.addWidget(QLabel("Số điện thoại:"), 0, 2)
        self.txt_contact = QLineEdit()
        self.txt_contact.setStyleSheet("padding:10px; border-radius:8px; border:1px solid #ccc;")
        cgrid.addWidget(self.txt_contact, 0, 3)
        cvbox.addWidget(cust_frame)

        # Giỏ hàng
        cart_header = QLabel("GIỎ HÀNG")
        cart_header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        cart_header.setStyleSheet("background:#e91e63; color:white; padding:15px; border-radius:12px 12px 0 0;")
        cart_header.setAlignment(Qt.AlignCenter)
        cvbox.addWidget(cart_header)

        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(4)
        self.cart_table.setHorizontalHeaderLabels(["Mã", "Tên SP", "Giá", "SL"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cart_table.setStyleSheet("font-size: 13px;")
        self.cart_table.cellClicked.connect(self.select_cart_item)
        cvbox.addWidget(self.cart_table)

        # Thêm sản phẩm vào giỏ
        add_frame = QFrame()
        add_frame.setStyleSheet("background:#f0f8ff; border-radius:10px; padding:10px;")
        add_grid = QGridLayout(add_frame)
        self.txt_pid = QLineEdit(); self.txt_pid.setReadOnly(True)
        self.txt_pname = QLineEdit(); self.txt_pname.setReadOnly(True)
        self.txt_price = QLineEdit(); self.txt_price.setReadOnly(True)
        self.spin_qty = QSpinBox()
        self.spin_qty.setRange(1, 1000)
        self.spin_qty.setStyleSheet("padding:8px;")

        add_grid.addWidget(QLabel("Mã SP:"), 0, 0)
        add_grid.addWidget(self.txt_pid, 0, 1)
        add_grid.addWidget(QLabel("Tên SP:"), 0, 2)
        add_grid.addWidget(self.txt_pname, 0, 3)
        add_grid.addWidget(QLabel("Giá:"), 1, 0)
        add_grid.addWidget(self.txt_price, 1, 1)
        add_grid.addWidget(QLabel("Số lượng:"), 1, 2)
        add_grid.addWidget(self.spin_qty, 1, 3)

        btn_add = QPushButton("Thêm / Cập nhật")
        btn_add.clicked.connect(self.add_update_cart)
        btn_add.setStyleSheet("""
            background:#4361ee; color:white; font-weight:bold;
            padding:12px; border-radius:10px; font-size:14px;
        """)
        add_grid.addWidget(btn_add, 0, 4, 2, 1)
        cvbox.addWidget(add_frame)

        body_layout.addWidget(center, 4)

        # ------------------ CỘT PHẢI: HÓA ĐƠN ------------------
        right = QFrame()
        right.setStyleSheet("background:white; border-radius:15px; border:1px solid #ddd;")
        rvbox = QVBoxLayout(right)

        # CỘT PHẢI: Tiêu đề hóa đơn
        bill_header = QLabel("HÓA ĐƠN KHÁCH HÀNG")
        bill_header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        bill_header.setStyleSheet("background:#9c27b0; color:white; padding:15px; border-radius:12px 12px 0 0;")
        bill_header.setAlignment(Qt.AlignCenter)
        rvbox.addWidget(bill_header)

        self.txt_bill_area = QTextEdit()
        self.txt_bill_area.setFont(QFont("Courier New", 11))
        self.txt_bill_area.setStyleSheet("""
            border: 2px solid #ddd; border-radius: 10px;
            background: #1e1e1e; color: #00ff00; padding: 10px;
        """)
        rvbox.addWidget(self.txt_bill_area)

        # Nút chức năng
        btn_box = QHBoxLayout()
        btn_generate = QPushButton("TẠO HÓA ĐƠN")
        btn_generate.clicked.connect(self.generate_bill)
        btn_generate.setStyleSheet("background:#ff6b6b; color:white; padding:15px; font-weight:bold; border-radius:12px; font-size:15px;")

        btn_print = QPushButton("IN HÓA ĐƠN")
        btn_print.clicked.connect(self.save_bill_to_file)
        btn_print.setStyleSheet("background:#4ecdc4; color:white; padding:15px; font-weight:bold; border-radius:12px; font-size:15px;")

        btn_clear = QPushButton("XÓA TẤT CẢ")
        btn_clear.clicked.connect(self.clear_all)
        btn_clear.setStyleSheet("background:#ff4757; color:white; padding:15px; font-weight:bold; border-radius:12px; font-size:15px;")

        btn_box.addWidget(btn_generate)
        btn_box.addWidget(btn_print)
        btn_box.addWidget(btn_clear)
        rvbox.addLayout(btn_box)

        body_layout.addWidget(right, 3)

        # ===================== FOOTER =====================
        footer = QLabel("© 2025 Inventory Management System | Phát triển bởi Nishant Gupta | Liên hệ: 9899459288")
        footer.setStyleSheet("background:#2c3e50; color:#bdc3c7; padding:12px; font-size:12px;")
        footer.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(footer)

    # ===================== CÁC HÀM CHỨC NĂNG =====================
    def save_bill_to_file(self):
        if not self.cart_list:
            QMessageBox.information(self, "Info", "Generate bill first")
            return

        # Thư mục lưu hóa đơn
        folder = "bill"
        if not os.path.exists(folder):
            os.makedirs(folder)  # tạo folder nếu chưa có

        # Tên file có thể dùng timestamp để không bị trùng
        import datetime
        timestamp = int(time.strftime("%H%M%S")) + int(time.strftime("%d%m%Y"))
        file_path = os.path.join(folder, f"{timestamp}.txt")

        # Ghi file với encoding UTF-8 để hỗ trợ tiếng Việt
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.txt_bill_area.toPlainText())
            QMessageBox.information(self, "Thành công", f"Lưu hóa đơn thành công:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu file:\n{str(e)}")

    def start_clock(self):
        def update():
            now = time.strftime("%d/%m/%Y | %H:%M:%S")
            self.lbl_clock.setText(f"Chào mừng đến với hệ thống quản lý kho  |  {now}")

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(update)
        self.clock_timer.start(1000)
        update()

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
            print(result)
            return result if result is not None else []
        except Exception as e:
            QMessageBox.critical(self, "Lỗi CSDL", f"Query failed:\n{str(e)}\nQuery: {query}")
            return []

    def load_products(self):
        rows = self.execute_db("SELECT pid,name,price,qty,status FROM product WHERE status='Active'", fetch=True)
        self.product_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                self.product_table.setItem(r, c, item)

    def search_product(self):
        keyword = self.txt_search.text().strip()
        if not keyword:
            self.load_products()
            return
        rows = self.execute_db(
            "SELECT pid,name,price,qty,status FROM product WHERE name LIKE ? AND status='Active'",
            (f"%{keyword}%",), fetch=True)
        self.product_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                self.product_table.setItem(r, c, QTableWidgetItem(str(val)))

    def select_product(self, row, col):
        self.txt_pid.setText(self.product_table.item(row,0).text())
        self.txt_pname.setText(self.product_table.item(row,1).text())
        self.txt_price.setText(self.product_table.item(row,2).text())
        stock = int(self.product_table.item(row,3).text())
        self.spin_qty.setMaximum(stock)
        self.spin_qty.setValue(1)

    def select_cart_item(self, row, col):
        self.txt_pid.setText(self.cart_table.item(row,0).text())
        self.txt_pname.setText(self.cart_table.item(row,1).text())
        self.txt_price.setText(self.cart_table.item(row,2).text())
        self.spin_qty.setValue(int(self.cart_table.item(row,3).text()))

    def add_update_cart(self):
        pid = self.txt_pid.text()
        if not pid:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn sản phẩm!")
            return
        name = self.txt_pname.text()
        price = float(self.txt_price.text())
        qty = self.spin_qty.value()

        for i, item in enumerate(self.cart_list):
            if item[0] == pid:
                self.cart_list[i][3] += qty
                break
        else:
            self.cart_list.append([pid, name, price, qty])

        self.update_cart()

    def update_cart(self):
        self.cart_table.setRowCount(len(self.cart_list))
        for r, item in enumerate(self.cart_list):
            for c in range(4):
                self.cart_table.setItem(r, c, QTableWidgetItem(str(item[c])))

    def generate_bill(self):
        if not self.cart_list:
            QMessageBox.warning(self, "Lỗi", "Giỏ hàng trống!")
            return

        # --- Thông tin hóa đơn ---
        bill_lines = [
            "          XYZ INVENTORY SYSTEM",
            "   Địa chỉ: 123 Đường ABC, TP.HCM",
            "   Hotline: 0989 945 9288",
            "=" * 55,
            f"Khách: {self.txt_cname.text().strip() or 'Khách lẻ':<35}",
            f"SĐT  : {self.txt_contact.text().strip() or 'Không':<35}",
            f"Ngày : {time.strftime('%d/%m/%Y %H:%M:%S')}",
            "=" * 55,
            f"{'Sản phẩm':<28} {'SL':>5} {'Đơn giá':>12} {'Thành tiền':>12}",
            "-" * 60
        ]

        total = 0
        updated_count = 0

        # --- Xử lý từng sản phẩm trong giỏ ---
        for item in self.cart_list:
            pid = int(item[0])  # PID là số nguyên
            name = str(item[1])
            price = float(item[2])
            qty = int(item[3])
            line_total = price * qty
            total += line_total

            # Cắt tên dài để không lệch cột
            display_name = (name[:25] + "...") if len(name) > 28 else name.ljust(28)
            bill_lines.append(f"{display_name} {qty:>5} {price:>12,.0f} {line_total:>12,.0f}")

            # --- Cập nhật tồn kho ---
            try:
                result = self.execute_db(
                    "SELECT qty FROM product WHERE pid = %s",
                    (pid,),  # tuple chứa int
                    fetch=True
                )
                print(result)
                if result:
                    current_qty = int(result[0][0])
                    new_qty = max(0, current_qty - qty)
                    status = "Inactive" if new_qty == 0 else "Active"

                    self.execute_db(
                        "UPDATE product SET qty = %s, status = %s WHERE pid = %s",
                        (new_qty, status, pid)
                    )
                    updated_count += 1
                else:
                    bill_lines.append(f"  [KHÔNG TÌM THẤY SP PID={pid}]")
            except Exception as e:
                bill_lines.append(f"  [LỖI DB: {e}]")

        # --- Tính thanh toán ---
        discount = total * 0.05
        net_pay = total - discount

        bill_lines.extend([
            "-" * 60,
            f"{'TỔNG TIỀN':>48}: {total:>12,.0f} ₫",
            f"{'GIẢM GIÁ 5%':>48}: {discount:>12,.0f} ₫",
            f"{'THÀNH TIỀN':>48}: {net_pay:>12,.0f} ₫",
            "=" * 60,
            "       CẢM ƠN QUÝ KHÁCH ĐÃ MUA HÀNG!",
            "           HẸN GẶP LẠI!",
            ""
        ])

        # --- Hiển thị hóa đơn ---
        self.txt_bill_area.setPlainText("\n".join(bill_lines))
        QMessageBox.information(
            self, "Thành công!",
            f"Hóa đơn đã tạo!\n"
            f"• Tổng tiền: {total:,.0f} ₫\n"
            f"• Cập nhật kho: {updated_count}/{len(self.cart_list)} sản phẩm"
        )

        # --- Tải lại sản phẩm ---
        self.load_products()

    def print_bill(self):
        if not self.txt_bill_area.toPlainText().strip():
            QMessageBox.information(self, "Thông báo", "Chưa có hóa đơn để in!")
            return
        path = tempfile.mktemp(suffix=".txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.txt_bill_area.toPlainText())
        os.startfile(path, "print")

    def clear_all(self):
        if QMessageBox.question(self, "Xác nhận", "Xóa toàn bộ giỏ hàng?") == QMessageBox.Yes:
            self.cart_list.clear()
            self.update_cart()
            self.txt_bill_area.clear()
            self.txt_cname.clear()
            self.txt_contact.clear()
            self.txt_pid.clear()
            self.txt_pname.clear()
            self.txt_price.clear()
            self.spin_qty.setValue(1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = BillWindow()
    win.show()
    sys.exit(app.exec())


