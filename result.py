# result_window.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap


class ResultWindow(QWidget):
    def __init__(self, image_path=None, result_text=""):
        super().__init__()
        self.setWindowTitle("결과 창")
        self.setGeometry(150, 150, 600, 400)

        layout = QVBoxLayout()

        # 이미지 표시
        if image_path:
            pixmap = QPixmap(image_path)
            img_label = QLabel()
            img_label.setPixmap(pixmap.scaledToWidth(500))
            layout.addWidget(img_label)

        # 결과 텍스트 표시
        result_label = QLabel(result_text)
        layout.addWidget(result_label)

        self.setLayout(layout)