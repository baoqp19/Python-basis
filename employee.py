import sys
import re
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton,
                               QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout,
                               QVBoxLayout, QGridLayout, QMessageBox)
from create_db import get_connection
from Toast import *
class EmployeeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Management System | Employee")
        self.setGeometry(320, 220, 1100, 500)
        self.init_ui()
        self.show_employees()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # -------- Search bar --------
        search_layout = QHBoxLayout()
        self.cmb_search = QComboBox()
        self.cmb_search.setStyleSheet("""
            QComboBox {
                background-color: #f8f9fa;
                color: #212529;
                padding: 6px;
                border: 1px solid #ced4da;
                border-radius: 6px;
            }
            QComboBox:hover {
                border: 1px solid #0d6efd;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #212529;
                selection-background-color: #0d6efd;
                selection-color: #ffffff;
            }
            QComboBox::item:selected {
                color: #ffffff;
                background-color: #0d6efd;
            }
        """)
        self.cmb_search.addItems(["Select", "email", "name", "contact"])
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Enter search text...")
        self.txt_search.setStyleSheet("""
            QLineEdit {
                background-color: #f8f9fa;
                color: #212529;
                padding: 6px 8px;
                border: 1px solid #ced4da;
                border-radius: 6px;
                selection-background-color: #0d6efd;
                selection-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #0d6efd;
                background-color: white;
            }
        """)

        self.btn_search = QPushButton("Search")
        self.btn_search.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
                color: white;
                font-weight: bold;
                padding: 6px 14px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
            QPushButton:pressed {
                background-color: #0a58ca;
            }
        """)
        self.btn_search.clicked.connect(self.search_employee)

        search_layout.addWidget(self.cmb_search)
        search_layout.addWidget(self.txt_search)
        search_layout.addWidget(self.btn_search)
        main_layout.addLayout(search_layout)

        # -------- Form layout --------
        form_layout = QGridLayout()

        # Spacing đẹp – không bị dính label/input
        form_layout.setVerticalSpacing(14)
        form_layout.setHorizontalSpacing(20)
        form_layout.setContentsMargins(10, 10, 10, 10)

        labels = [
            "Emp ID", "Name", "Email", "Gender", "Contact", "D.O.B", "D.O.J",
            "Password", "User Type", "Address", "Salary"
        ]

        self.inputs = {}

        for i, label in enumerate(labels):
            # ---- Label ----
            lbl = QLabel(label)
            lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
            lbl.setStyleSheet("""
                color: #212529;
                padding-bottom: 4px;
                font-weight: bold;
            """)
            form_layout.addWidget(lbl, i // 2, (i % 2) * 2)

            # ---- Input ----
            if label == "Gender":
                inp = QComboBox()
                inp.addItems(["Select", "Male", "Female", "Other"])
            elif label == "User Type":
                inp = QComboBox()
                inp.addItems(["Admin", "Employee"])
            elif label == "Address":
                inp = QTextEdit()
                inp.setFixedHeight(60)
                inp.setPlaceholderText("Enter employee address...")
            elif label == "Emp ID":
                inp = QLineEdit()
                inp.setReadOnly(True)
                inp.setPlaceholderText("Auto generated")
            elif label in ["D.O.B", "D.O.J"]:
                inp = QLineEdit()
                inp.setPlaceholderText("YYYY-MM-DD")
            elif label == "Salary":
                inp = QLineEdit()
                inp.setPlaceholderText("Enter salary")
            elif label == "Password":
                inp = QLineEdit()
                inp.setEchoMode(QLineEdit.Password)
                inp.setPlaceholderText("Enter password")
            else:
                inp = QLineEdit()
                inp.setPlaceholderText(f"Enter {label.lower()}")

            # ---- INPUT STYLE CHUNG ----
            inp.setStyleSheet("""
                QLineEdit, QTextEdit, QComboBox {
                    background-color: #ffffff;
                    color: #212529;
                    border: 1px solid #ced4da;
                    border-radius: 8px;
                    padding: 6px 10px;
                    font-size: 14px;
                }

                QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                    border: 1px solid #0d6efd;
                    box-shadow: 0 0 6px rgba(13,110,253,0.3);
                }

                QTextEdit {
                    padding: 8px;
                }

                /* Đảm bảo chữ trong dropdown là đen */
                QComboBox QAbstractItemView {
                    background-color: #ffffff;
                    color: #212529;
                    selection-background-color: #0d6efd;
                    selection-color: #ffffff;
                }
            """)

            self.inputs[label] = inp
            form_layout.addWidget(inp, i // 2, 1 + (i % 2))

        main_layout.addLayout(form_layout)

        # -------- Buttons --------
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Save")
        self.btn_add.setStyleSheet("background-color:#0d6efd; color:white; font-weight:bold; border-radius:5px;")
        self.btn_add.clicked.connect(self.add_employee)

        self.btn_update = QPushButton("Update")
        self.btn_update.setStyleSheet("background-color:#198754; color:white; font-weight:bold; border-radius:5px;")
        self.btn_update.clicked.connect(self.update_employee)

        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setStyleSheet("background-color:#dc3545; color:white; font-weight:bold; border-radius:5px;")
        self.btn_delete.clicked.connect(self.delete_employee)

        self.btn_clear = QPushButton("Clear")
        self.btn_clear.setStyleSheet("background-color:#6c757d; color:white; font-weight:bold; border-radius:5px;")
        self.btn_clear.clicked.connect(self.clear_form)

        for btn in [self.btn_add, self.btn_update, self.btn_delete, self.btn_clear]:
            btn.setFixedHeight(30)
            btn.setFixedWidth(100)
            btn_layout.addWidget(btn)

        main_layout.addLayout(btn_layout)

        # -------- Employee Table --------
        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels(labels[:-1] + ["Address"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f8f9fa;
                color: #212529;
                gridline-color: #dee2e6;
                font-size: 11pt;
            }
            QHeaderView::section {
                background-color: #0d6efd;
                color: #ffffff;
                font-weight: bold;
                padding: 4px;
                border: 1px solid #dee2e6;
            }
            QTableWidget::item:selected {
                background-color: #cfe2ff;
                color: #212529;
            }
        """)
        self.table.cellClicked.connect(self.load_from_table)
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

    def toast(self, msg):
        Toast(msg, self).show()

    def toast_error(self, msg):
        Toast(msg, self, error=True).show()

    # -------- CRUD Methods --------
    def add_employee(self):

        salary_text = self.inputs["Salary"].text().strip()
        # Kiểm tra có phải số (có thể là float hoặc int)
        try:
            salary = float(salary_text)
            if salary < 0:
                self.toast_error("Lương không thể âm ! ")
                return
        except ValueError:
            self.toast_error("Lương phải là số ! ")
            return

        email_text = self.inputs["Email"].text().strip()

        # Regex cơ bản để kiểm tra email hợp lệ
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email_text):
            self.toast_error("Email không đúng định dạng! ")
            return

        try:
            con = get_connection()
            cur = con.cursor()

            cur.execute("""INSERT INTO employee(name, email, gender, contact, dob, doj, pass, utype, address, salary)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (
                            self.inputs["Name"].text(),
                            email_text,
                            self.inputs["Gender"].currentText() if self.inputs[
                                                                       "Gender"].currentText() != "Select" else "",
                            self.inputs["Contact"].text(),
                            self.inputs["D.O.B"].text(),
                            self.inputs["D.O.J"].text(),
                            self.inputs["Password"].text(),
                            self.inputs["User Type"].currentText(),
                            self.inputs["Address"].toPlainText(),
                            salary
                        ))

            con.commit()

            self.toast("Employee added successfully!")
            self.clear_form()
            self.show_employees()

        except Exception as e:
            self.toast_error(str(e))

    def show_employees(self):
        try:
            con = get_connection()
            cur = con.cursor()
            cur.execute("SELECT * FROM employee")
            rows = cur.fetchall()
            self.table.setRowCount(0)
            for row_data in rows:
                row = self.table.rowCount()
                self.table.insertRow(row)
                for col, data in enumerate(row_data):
                    self.table.setItem(row, col, QTableWidgetItem(str(data)))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def load_from_table(self, row, col):
        self.inputs["Emp ID"].setText(self.table.item(row, 0).text())
        self.inputs["Name"].setText(self.table.item(row, 1).text())
        self.inputs["Email"].setText(self.table.item(row, 2).text())
        self.inputs["Gender"].setCurrentText(self.table.item(row, 3).text())
        self.inputs["Contact"].setText(self.table.item(row, 4).text())
        self.inputs["D.O.B"].setText(self.table.item(row, 5).text())
        self.inputs["D.O.J"].setText(self.table.item(row, 6).text())
        self.inputs["Password"].setText(self.table.item(row, 7).text())
        self.inputs["User Type"].setCurrentText(self.table.item(row, 8).text())
        self.inputs["Address"].setText(self.table.item(row, 9).text())
        self.inputs["Salary"].setText(self.table.item(row, 10).text())

    def update_employee(self):

        salary_text = self.inputs["Salary"].text().strip()
        # Kiểm tra có phải số (có thể là float hoặc int)
        try:
            salary = float(salary_text)
            if salary < 0:
                self.toast_error("Lương không thể âm ! ")
                return
        except ValueError:
            self.toast_error("Lương phải là số ! ")
            return

        email_text = self.inputs["Email"].text().strip()

        # Regex cơ bản để kiểm tra email hợp lệ
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email_text):
            self.toast_error("Email không đúng định dạng! ")
            return

        try:
            if not self.inputs["Emp ID"].text():
                self.toast_error("Lựa cho nhân viên cập nhật!")
                return
            con = get_connection()
            cur = con.cursor()
            cur.execute("""UPDATE employee SET
                           name=%s,email=%s,gender=%s,contact=%s,dob=%s,doj=%s,
                           pass=%s,utype=%s,address=%s,salary=%s WHERE eid=%s""", (
                self.inputs["Name"].text(),
                email_text,
                self.inputs["Gender"].currentText(),
                self.inputs["Contact"].text(),
                self.inputs["D.O.B"].text(),
                self.inputs["D.O.J"].text(),
                self.inputs["Password"].text(),
                self.inputs["User Type"].currentText(),
                self.inputs["Address"].toPlainText(),
                salary_text,
                self.inputs["Emp ID"].text()
            ))

            con.commit()
            self.toast("Nhân viện đã được cập nhật!")
            self.clear_form()
            self.show_employees()
        except Exception as e:
            self.toast_error(str(e))

    def delete_employee(self):
        try:
            emp_id = self.inputs["Emp ID"].text().strip()

            if not emp_id:
                self.toast_error("⚠️ Select an employee to delete!")
                return

            # ----- Custom Dark Confirm Box -----
            msg = QMessageBox(self)
            msg.setWindowTitle("Confirm")
            msg.setText("<span style='color:black; font-size:14px;'>Do you really want to delete?</span>")
            msg.setIcon(QMessageBox.Question)
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #1e1e1e;
                    border: 2px solid #3a3a3a;
                    border-radius: 10px;
                }
                QLabel {
                    color: white;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #3a3a3a;
                    color: white;
                    padding: 6px 14px;
                    border-radius: 6px;
                    font-weight: bold;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #505050;
                }
                QPushButton:pressed {
                    background-color: #606060;
                }
            """)

            reply = msg.exec()

            # ----- User confirmed delete -----
            if reply == QMessageBox.Yes:
                con = get_connection()
                cur = con.cursor()
                cur.execute("DELETE FROM employee WHERE eid=%s", (emp_id,))
                con.commit()

                self.toast("✔ Employee deleted successfully!")
                self.clear_form()
                self.show_employees()

        except Exception as e:
            self.toast_error(f"❌ Error: {str(e)}")

    def clear_form(self):
        for key, widget in self.inputs.items():
            if isinstance(widget, QLineEdit):
                widget.clear()
            elif isinstance(widget, QTextEdit):
                widget.clear()
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)
        self.show_employees()

    def search_employee(self):
        try:
            field = self.cmb_search.currentText()
            text = self.txt_search.text()
            if field == "Select" or not text:
                QMessageBox.warning(self, "Error", "Select search field and enter search text!")
                return
            con = get_connection()
            cur = con.cursor()
            query = f"SELECT * FROM employee WHERE {field} LIKE %s"
            cur.execute(query, (f"%{text}%",))
            rows = cur.fetchall()
            self.table.setRowCount(0)
            for row_data in rows:
                row = self.table.rowCount()
                self.table.insertRow(row)
                for col, data in enumerate(row_data):
                    self.table.setItem(row, col, QTableWidgetItem(str(data)))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EmployeeApp()
    window.show()
    sys.exit(app.exec())  # exec() cho PySide6
