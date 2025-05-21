from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class ResultWindow(QWidget):
    def __init__(self, image_paths):
        super().__init__()
        self.setWindowTitle("불량 이미지 결과 보기")
        self.setGeometry(300, 100, 1000, 700)

        self.image_paths = image_paths if isinstance(image_paths, list) else [image_paths]
        self.current_page = 0
        self.items_per_page = 6  # 페이지당 6장

        self.setStyleSheet("""
            QWidget {
                background-color: #FFF;
                font-family: 'Arial', sans-serif;
            }
            QPushButton {
                background-color: #F3B72E;
                color: white;
                font-size: 14px;
                padding: 10px 20px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #104681;
            }
            QLabel {
                font-size: 13px;
                color: #333;
            }
        """)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.grid_layout = QGridLayout()
        self.main_layout.addLayout(self.grid_layout)

        # 네비게이션 영역
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("<")
        self.prev_button.clicked.connect(self.show_previous_page)

        self.page_label = QLabel()
        self.next_button = QPushButton(">")
        self.next_button.clicked.connect(self.show_next_page)

        self.back_button = QPushButton("메인으로")
        self.back_button.clicked.connect(self.close)

        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.page_label)
        nav_layout.addWidget(self.next_button)
        nav_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding))
        nav_layout.addWidget(self.back_button)

        self.main_layout.addLayout(nav_layout)

        self.update_page()

    def update_page(self):
        # 기존 위젯 제거
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        # 이미지 1장일 경우 중앙 정렬로 표시
        if len(self.image_paths) == 1:
            image_label = QLabel()
            pixmap = QPixmap(self.image_paths[0]).scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignCenter)

            text_label = QLabel("불량품 감지됨\n반지름: 추후 표시")
            text_label.setAlignment(Qt.AlignCenter)
            text_label.setWordWrap(True)

            container_layout = QVBoxLayout()
            container_layout.setAlignment(Qt.AlignCenter)
            container_layout.addWidget(image_label)
            container_layout.addWidget(text_label)

            container_widget = QWidget()
            container_widget.setLayout(container_layout)

            self.grid_layout.addWidget(container_widget, 0, 0, 1, 3)  # 가운데 정렬 (colspan 3)

            self.page_label.setText("1 / 1 페이지")
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
            return

        # 여러 이미지일 경우 페이징
        start = self.current_page * self.items_per_page
        end = min(start + self.items_per_page, len(self.image_paths))
        current_images = self.image_paths[start:end]

        for idx, path in enumerate(current_images):
            image_label = QLabel()
            pixmap = QPixmap(path).scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignCenter)

            text_label = QLabel("불량품 감지됨\n반지름: 추후 표시")
            text_label.setAlignment(Qt.AlignCenter)
            text_label.setWordWrap(True)
            text_label.setFixedWidth(200)

            container_layout = QVBoxLayout()
            container_widget = QWidget()
            container_layout.addWidget(image_label)
            container_layout.addWidget(text_label)
            container_widget.setLayout(container_layout)

            row = idx // 3
            col = idx % 3
            self.grid_layout.addWidget(container_widget, row, col)

        total_pages = (len(self.image_paths) - 1) // self.items_per_page + 1
        self.page_label.setText(f"{self.current_page + 1} / {total_pages} 페이지")
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page < total_pages - 1)

    def show_previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_page()

    def show_next_page(self):
        max_page = (len(self.image_paths) - 1) // self.items_per_page
        if self.current_page < max_page:
            self.current_page += 1
            self.update_page()
