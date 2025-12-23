import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QGridLayout,
    QMessageBox, QHeaderView, QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from create_db import get_connection
from Toast import *

class ProductClass(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản Lý Sản Phẩm")
        self.resize(1400, 750)

        self.txt_pid = QLineEdit(self)
        self.cat_list = []
        self.sup_list = []
        self.fetch_cat_sup()

        # ==================== MAIN LAYOUT ====================
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(25)

        # ==================== LEFT: FORM ====================
        left_frame = QFrame()
        left_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(25, 25, 25, 25)
        left_layout.setSpacing(20)
        main_layout.addWidget(left_frame, 2)

        # Tiêu đề
        title = QLabel("THÔNG TIN SẢN PHẨM")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1e40af, stop:1 #3b82f6);
            color: white; padding: 16px; border-radius: 12px;
        """)
        left_layout.addWidget(title)

        # Grid form
        grid = QGridLayout()
        grid.setVerticalSpacing(15)
        grid.setHorizontalSpacing(15)
        left_layout.addLayout(grid)

        labels = ["Danh mục", "Nhà cung cấp", "Tên sản phẩm", "Giá", "Số lượng", "Trạng thái"]
        row = 0
        for label_text in labels:
            lbl = QLabel(label_text + ":")
            lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
            lbl.setStyleSheet("color: #1e293b;")
            grid.addWidget(lbl, row, 0)

            if label_text == "Danh mục":
                self.cmb_cat = QComboBox()
                self.cmb_cat.addItems(self.cat_list)

                # Đổi chữ đen + nền trắng cho cả combobox và dropdown
                self.cmb_cat.setStyleSheet("""
                    QComboBox {
                        color: black;                  /* chữ màu đen */
                        background-color: white;       /* nền trắng cho phần hiển thị */
                        border: 1px solid #ccc;        /* viền nhẹ nếu muốn */
                        padding: 4px;
                    }
                    QComboBox QAbstractItemView {
                        color: black;                  /* chữ đen trong dropdown */
                        background-color: white;       /* nền trắng cho dropdown */
                        selection-background-color: #3399FF;  /* nền xanh khi chọn item */
                        selection-color: white;        /* chữ trắng khi chọn */
                        border: 1px solid #ccc;
                    }
                    QComboBox::drop-down {
                        border: 0px;
                        width: 20px;
                    }
                    QComboBox::down-arrow {
                        image: none;  /* hoặc url() nếu muốn icon mũi tên tùy chỉnh */
                    }
                """)

                self.style_combo(self.cmb_cat)
                grid.addWidget(self.cmb_cat, row, 1)
            elif label_text == "Nhà cung cấp":
                self.cmb_sup = QComboBox()
                self.cmb_sup.addItems(self.sup_list)
                self.style_combo(self.cmb_sup)
                grid.addWidget(self.cmb_sup, row, 1)
            elif label_text == "Trạng thái":
                self.cmb_status = QComboBox()
                self.cmb_status.addItems(["Active", "Inactive"])
                self.style_combo(self.cmb_status)
                self.cmb_status.setCurrentText("Active")
                grid.addWidget(self.cmb_status, row, 1)
            else:
                txt = QLineEdit()
                txt.setPlaceholderText(f"Nhập {label_text.lower()}...")
                self.style_input(txt)
                if label_text == "Tên sản phẩm":
                    self.txt_name = txt
                elif label_text == "Giá":
                    self.txt_price = txt
                elif label_text == "Số lượng":
                    self.txt_qty = txt
                grid.addWidget(txt, row, 1)
            row += 1

        # Nút thao tác
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_save = self.create_button("Lưu", "#10b981", self.add_product)
        btn_update = self.create_button("Cập nhật", "#3b82f6", self.update_product)
        btn_delete = self.create_button("Xóa", "#ef4444", self.delete_product)
        btn_clear = self.create_button("Làm mới", "#64748b", self.clear_form)

        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_update)
        btn_layout.addWidget(btn_delete)
        btn_layout.addWidget(btn_clear)
        left_layout.addLayout(btn_layout)

        # ==================== RIGHT: SEARCH + TABLE ====================
        right_frame = QFrame()
        right_frame.setStyleSheet("background: white; border-radius: 16px; border: 1px solid #e2e8f0;")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(25, 25, 25, 25)
        right_layout.setSpacing(20)
        main_layout.addWidget(right_frame, 3)

        # Thanh tìm kiếm
        search_bar = QHBoxLayout()
        search_bar.addWidget(QLabel("Tìm kiếm theo:"))
        self.cmb_search = QComboBox()
        self.cmb_search.addItems(["Chọn", "Category", "Supplier", "name"])
        self.style_combo(self.cmb_search, width=180)

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Nhập từ khóa tìm kiếm...")
        self.style_input(self.txt_search)

        btn_search = QPushButton("Tìm")
        btn_search.setFixedHeight(48)
        btn_search.setStyleSheet("""
            QPushButton {
                background: #3b82f6; color: white; font-weight: bold;
                border-radius: 12px; padding: 0 30px;
            }
            QPushButton:hover { background: #2563eb; }
        """)
        btn_search.clicked.connect(self.search_product)

        search_bar.addWidget(self.cmb_search)
        search_bar.addWidget(self.txt_search)
        search_bar.addWidget(btn_search)
        search_bar.addStretch()
        right_layout.addLayout(search_bar)

        # Bảng dữ liệu
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Mã SP", "Danh mục", "Nhà cung cấp", "Tên sản phẩm", "Giá", "SL", "Trạng thái"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setStyleSheet("QHeaderView::section { background: #1e40af; color: white; font-weight: bold; padding: 12px; }")

        self.table.setStyleSheet("""
            QTableWidget {
                border: none; border-radius: 12px; gridline-color: #e2e8f0;
                background: white; font-size: 13px;
            }
            QTableWidget::item { padding: 10px; color: #1e293b; }
            QTableWidget::item:selected { background: #dbeafe; color: #1e40af; }
        """)
        self.table.cellClicked.connect(self.load_from_table)
        right_layout.addWidget(self.table)

        # Load dữ liệu
        self.show_data()

    # -------- Database Methods --------
    def toast(self, msg):
        Toast(msg, self).show()

    def toast_error(self, msg):
        Toast(msg, self, error=True).show()

    def style_input(self, widget):
        widget.setFixedHeight(48)
        widget.setStyleSheet("""
            QLineEdit {
                border: 2px solid #cbd5e1;
                border-radius: 12px;
                padding: 0 16px;
                font-size: 14px;
                background: white;
                color: black;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
            }
        """)

    def style_combo(self, widget, width=None):
        widget.setFixedHeight(48)
        if width:
            widget.setFixedWidth(width)
        widget.setStyleSheet("""
            QComboBox {
                border:  | 2px solid #cbd5e1;
                border-radius: 12px;
                padding: 0 16px;
                font-size: 14px;
                background: white;
                color: black;
            }
            QComboBox:focus {
                border: 2px solid #3b82f6;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                width: 12px; height: 12px;
                margin-right: 10px;
            }
        """)


    def create_button(self, text, color, callback):
        btn = QPushButton(text)
        btn.setFixedHeight(48)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {color};
                color: white;
                font-weight: bold;
                border-radius: 12px;
                padding: 0 28px;
                font-size: 14px;
            }}
            QPushButton:hover {{ background: {self.darken_color(color)}; }}
            QPushButton:pressed {{ background: {self.darken_color(color, 0.8)}; }}
        """)
        btn.clicked.connect(callback)
        return btn

    def darken_color(self, hex_color, factor=0.8):
        import colorsys
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        r, g, b = [x / 255.0 for x in rgb]
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        l = max(0, l * factor)
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"

    def show_warning(self, message="All fields are required"):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Cảnh báo")
        msg.setText(f"<b style='color:#d32f2f; font-size:14px;'>{message}</b>")
        msg.setInformativeText("Vui lòng kiểm tra và điền đầy đủ các trường thông tin.")

        # Nút đẹp hơn
        msg.setStandardButtons(QMessageBox.Ok)
        msg.button(QMessageBox.Ok).setText("Đã hiểu")

        # Style siêu đẹp đây nè
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: Segoe UI, sans-serif;
                font-size: 13px;
            }
            QMessageBox QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                padding: 10px 24px;
                border-radius: 8px;
                font-weight: bold;
                min-width: 100px;
                font-size: 13px;
            }
            QMessageBox QPushButton:hover {
                background-color: #f44336;
            }
            QMessageBox QPushButton:pressed {
                background-color: #b71c1c;
            }
            QMessageBox QIcon {
                width: 48px;
                height: 48px;
            }
        """)

        msg.exec()

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
        cat_name = self.cmb_cat.currentText()
        sup_name = self.cmb_sup.currentText()
        name = self.txt_name.text().strip()
        price = self.txt_price.text().strip()
        qty = self.txt_qty.text().strip()
        status = self.cmb_status.currentText()

        if cat_name == "Select" or sup_name == "Select" or name == "":
            self.toast_error("Nhập đầy đủ thông tin")
            return

        try:
            con = get_connection()
            cur = con.cursor()

            # 🔹 Lấy category_id
            cur.execute("SELECT cid FROM category WHERE name=%s", (cat_name,))
            cat = cur.fetchone()
            if not cat:
                self.toast_error("Danh mục không tồn tại")
                return
            category_id = cat[0]

            # 🔹 Lấy supplier_id
            cur.execute("SELECT invoice FROM supplier WHERE name=%s", (sup_name,))
            sup = cur.fetchone()
            if not sup:
                self.toast_error("Nhà cung cấp không tồn tại")
                return
            supplier_id = sup[0]

            # 🔹 Check trùng tên sản phẩm
            cur.execute("SELECT pid FROM product WHERE name=%s", (name,))
            if cur.fetchone():
                QMessageBox.warning(self, "Lỗi", "Sản phẩm đã tồn tại")
            else:
                cur.execute("""
                            INSERT INTO product
                                (category_id, supplier_id, name, price, qty, status)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            """, (category_id, supplier_id, name, price, qty, status))

                con.commit()
                self.toast("Sản phẩm đã được thêm thành công")
                self.clear_form()
                self.show_data()

            con.close()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def show_data(self):
        try:
            con = get_connection()
            cur = con.cursor()

            cur.execute("""
                        SELECT p.pid,
                               c.name AS category,
                               s.name AS supplier,
                               p.name,
                               p.price,
                               p.qty,
                               p.status
                        FROM product p
                                 JOIN category c ON p.category_id = c.cid
                                 JOIN supplier s ON p.supplier_id = s.invoice
                        ORDER BY p.pid DESC
                        """)

            rows = cur.fetchall()
            self.table.setRowCount(0)

            for row_data in rows:
                row = self.table.rowCount()
                self.table.insertRow(row)
                for col, data in enumerate(row_data):
                    self.table.setItem(row, col, QTableWidgetItem(str(data)))

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
        if not self.var_pid:
            self.toast_error("Select a product to update")
            return

        try:
            con = get_connection()
            cur = con.cursor()

            # 🔹 Lấy category_id
            cur.execute("SELECT cid FROM category WHERE name=%s",
                        (self.cmb_cat.currentText(),))
            cat = cur.fetchone()
            if not cat:
                self.toast_error("Danh mục không tồn tại")
                return
            category_id = cat[0]

            # 🔹 Lấy supplier_id
            cur.execute("SELECT invoice FROM supplier WHERE name=%s",
                        (self.cmb_sup.currentText(),))
            sup = cur.fetchone()
            if not sup:
                self.toast_error("Nhà cung cấp không tồn tại")
                return
            supplier_id = sup[0]

            # 🔹 Update product
            cur.execute("""
                        UPDATE product
                        SET category_id=%s,
                            supplier_id=%s,
                            name=%s,
                            price=%s,
                            qty=%s,
                            status=%s
                        WHERE pid = %s
                        """, (
                            category_id,
                            supplier_id,
                            self.txt_name.text().strip(),
                            self.txt_price.text().strip(),
                            self.txt_qty.text().strip(),
                            self.cmb_status.currentText(),
                            self.var_pid
                        ))

            con.commit()
            QMessageBox.information(self, "Success", "Product Updated Successfully")
            self.clear_form()
            self.show_data()
            con.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def load_data(self):
        try:
            con = get_connection()
            cur = con.cursor()
            cur.execute("SELECT * FROM product")
            rows = cur.fetchall()

            if not rows:
                self.table.setRowCount(0)
                return

            self.table.setRowCount(len(rows))
            self.table.setColumnCount(len(rows[0]))

            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))

            # tự động chỉnh size cột
            self.table.resizeColumnsToContents()

            con.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Lỗi load dữ liệu:\n{str(e)}")

    def delete_product(self):
        reply = QMessageBox.question(
            self,
            "Xác nhận xóa",
            "Bạn có chắc chắn muốn xóa sản phẩm này không?\n\n"
            "Hành động này không thể hoàn tác.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        pid = self.var_pid  # hoặc tên widget bạn đang dùng

        if not pid:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn sản phẩm để xóa!")
            return

        try:
            con = get_connection()
            cur = con.cursor()
            cur.execute("DELETE FROM product WHERE pid = %s", (self.var_pid,))

            if cur.rowcount == 0:
                QMessageBox.warning(self, "Không tìm thấy", "Sản phẩm này đã bị xóa hoặc không tồn tại!")
            else:
                QMessageBox.information(self, "Thành công", "Xóa sản phẩm thành công!")
                con.commit()
                self.show_data()

            con.close()

            success_msg = QMessageBox(self)
            success_msg.setWindowTitle("Thành công")
            success_msg.setIcon(QMessageBox.Information)
            success_msg.setText("<b><span style='color:#4caf50;'>Xóa sản phẩm thành công!</span></b>")
            success_msg.setInformativeText(f"Đã xóa sản phẩm có mã: <b>{self.var_pid.get()}</b>")
            success_msg.setStandardButtons(QMessageBox.Ok)
            success_msg.button(QMessageBox.Ok).setText("Tuyệt vời!")

            # Style đẹp (dark mode sang trọng)
            success_msg.setStyleSheet("""
                QMessageBox {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    font-family: Segoe UI, sans-serif;
                }
                QMessageBox QLabel { color: #ffffff; }
                QMessageBox QPushButton {
                    background-color: #4caf50;
                    color: white;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-weight: bold;
                    min-width: 100px;
                }
                QMessageBox QPushButton:hover { background-color: #66bb6a; }
            """)

            success_msg.exec()

            # Cập nhật giao diện
            self.clear_form()
            self.show_data()
        finally:
            # Đảm bảo luôn đóng kết nối
            try:
                con.close()
            except:
                pass

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
        txt = self.txt_search.text().strip()

        if searchby == "Select" or txt == "":
            QMessageBox.warning(self, "Lỗi", "Lựa chọn trường để tìm kiếm")
            return

        # 🔒 Map hiển thị → cột DB (CHỐNG SQL Injection)
        column_map = {
            "Product Name": "p.name",
            "Category": "c.name",
            "Supplier": "s.name",
            "Status": "p.status"
        }

        if searchby not in column_map:
            QMessageBox.warning(self, "Lỗi", "Trường tìm kiếm không hợp lệ")
            return

        try:
            con = get_connection()
            cur = con.cursor()

            query = f"""
                SELECT 
                    p.pid,
                    c.name AS category,
                    s.name AS supplier,
                    p.name,
                    p.price,
                    p.qty,
                    p.status
                FROM product p
                JOIN category c ON p.category_id = c.cid
                JOIN supplier s ON p.supplier_id = s.invoice
                WHERE {column_map[searchby]} LIKE %s
                ORDER BY p.pid DESC
            """

            cur.execute(query, (f"%{txt}%",))
            rows = cur.fetchall()

            self.table.setRowCount(0)
            for row_data in rows:
                row = self.table.rowCount()
                self.table.insertRow(row)
                for col, data in enumerate(row_data):
                    self.table.setItem(row, col, QTableWidgetItem(str(data)))

            con.close()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))

    window = ProductClass()
    window.show()
    sys.exit(app.exec())