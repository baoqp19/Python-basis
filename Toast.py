# toast.py
# Toast notification siêu đẹp cho PySide6
# Dùng được ở mọi cửa sổ, tự động xếp chồng, có animation trượt + fade

from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QTimer
from PySide6.QtGui import QFont


class Toast(QLabel):
    """
    Toast notification đẹp như app hiện đại
    Cách dùng:
        from toast import Toast
        Toast("Thành công rồi!", parent=self).show()
        Toast("Lỗi rồi nhé!", parent=self, error=True, duration=4000).show()
    """
    _instances = []  # Quản lý các toast để xếp chồng

    def __init__(self, message: str, parent=None, duration: int = 3000, error: bool = False):
        super().__init__(message, parent)

        # Cấu hình cửa sổ toast
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # Màu nền: đỏ nếu lỗi, xanh nếu thành công
        bg_color = "#dc3545" if error else "#0d6efd"
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 14px 28px;
                border-radius: 12px;
                box-shadow: 0 6px 16px rgba(0, 0, 0, 0.18);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
        """)

        self.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.setAlignment(Qt.AlignCenter)
        self.adjustSize()

        self.duration = duration
        Toast._instances.append(self)

    def show(self):
        """Hiển thị toast với hiệu ứng trượt từ trên xuống"""
        super().show()
        self.raise_()

        if not self.parent():
            return

        margin = 20
        spacing = 10
        y_offset = margin

        # Tính vị trí cho toast mới (xếp chồng xuống dưới các toast cũ)
        for toast in Toast._instances:
            if toast != self and toast.isVisible():
                y_offset += toast.height() + spacing

        x = self.parent().width() - self.width() - margin

        start_rect = QRect(x, -self.height(), self.width(), self.height())
        end_rect = QRect(x, y_offset, self.width(), self.height())

        self.move(start_rect.topLeft())

        # Animation trượt xuống
        slide = QPropertyAnimation(self, b"geometry", self)
        slide.setDuration(600)
        slide.setEasingCurve(QEasingCurve.OutBack)
        slide.setStartValue(start_rect)
        slide.setEndValue(end_rect)
        slide.start()

        # Tự động fade out sau duration
        QTimer.singleShot(self.duration, self._start_fade_out)

    def _start_fade_out(self):
        """Bắt đầu hiệu ứng mờ dần và đóng"""
        fade = QPropertyAnimation(self, b"windowOpacity", self)
        fade.setDuration(500)
        fade.setStartValue(1.0)
        fade.setEndValue(0.0)
        fade.finished.connect(self.close)
        fade.start()

    def closeEvent(self, event):
        """Dọn dẹp khi đóng"""
        if self in Toast._instances:
            Toast._instances.remove(self)
        event.accept()

    def toast(self, msg):
        Toast(msg, self).show()

    def toast_error(self, msg):
        Toast(msg, self, error=True).show()