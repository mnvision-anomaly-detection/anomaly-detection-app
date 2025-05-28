from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QGridLayout,
    QHBoxLayout, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class ResultWindow(QWidget):
    def __init__(self, image_paths, results=None):
        super().__init__()
        self.setWindowTitle("불량 이미지 결과 보기")
        self.setGeometry(300, 100, 1000, 700)

        # 이미지 경로와 결과 리스트
        self.image_paths = image_paths if isinstance(image_paths, list) else [image_paths]
        self.results = results or [[] for _ in self.image_paths]
        self.current_page = 0
        self.items_per_page = 6

        # 스타일시트
        self.setStyleSheet("""
            QWidget { background-color: #FFF; font-family: 'Arial', sans-serif; }
            QPushButton { background-color: #F3B72E; color: white; font-size: 14px;
                          padding: 10px 20px; border-radius: 8px; border: none; }
            QPushButton:hover { background-color: #104681; }
            QLabel { font-size: 13px; color: #333; }
        """)

        # 레이아웃 설정
        self.main_layout = QVBoxLayout(self)
        self.grid_layout = QGridLayout()
        self.main_layout.addLayout(self.grid_layout)

        # 네비게이션 버튼
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
        nav_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        nav_layout.addWidget(self.back_button)
        self.main_layout.addLayout(nav_layout)

        self.update_page()

    def update_page(self):
        # 이전 결과 클리어
        for i in reversed(range(self.grid_layout.count())):
            w = self.grid_layout.itemAt(i).widget()
            if w: w.setParent(None)

        start = self.current_page * self.items_per_page
        end = min(start + self.items_per_page, len(self.image_paths))

        # 단일 이미지
        if len(self.image_paths) == 1:
            path, dets = self.image_paths[0], self.results[0]
            img_lbl = QLabel()
            img_lbl.setPixmap(QPixmap(path).scaled(300, 300, Qt.KeepAspectRatio))
            img_lbl.setAlignment(Qt.AlignCenter)

            info = [f"score:{d['anomaly_score']:.6f}, anomaly:{d['is_anomaly']}" for d in dets]
            text = "".join(info) if info else "이상 없음"
            txt_lbl = QLabel(text)
            txt_lbl.setAlignment(Qt.AlignCenter)
            txt_lbl.setWordWrap(True)

            container = QVBoxLayout()
            container.addWidget(img_lbl)
            container.addWidget(txt_lbl)
            w = QWidget(); w.setLayout(container)
            self.grid_layout.addWidget(w, 0, 0, 1, 3)

            self.page_label.setText("1 / 1 페이지")
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
            return

        # 다중 이미지
        for idx, idx_global in enumerate(range(start, end)):
            path = self.image_paths[idx_global]
            dets = self.results[idx_global]
            row, col = divmod(idx, 3)

            img_lbl = QLabel();
            img_lbl.setPixmap(QPixmap(path).scaled(200, 200, Qt.KeepAspectRatio))
            img_lbl.setAlignment(Qt.AlignCenter)

            info = [f"score:{d['anomaly_score']:.3f}, anomaly:{d['is_anomaly']}" for d in dets]
            if not info: info = ["이상 없음"]
            txt_lbl = QLabel("".join(info))
            txt_lbl.setAlignment(Qt.AlignCenter)
            txt_lbl.setWordWrap(True)
            txt_lbl.setFixedWidth(200)

            vbox = QVBoxLayout()
            vbox.addWidget(img_lbl)
            vbox.addWidget(txt_lbl)
            cell = QWidget(); cell.setLayout(vbox)
            self.grid_layout.addWidget(cell, row, col)

        total = (len(self.image_paths) - 1) // self.items_per_page + 1
        self.page_label.setText(f"{self.current_page + 1} / {total} 페이지")
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page < total - 1)

    def show_previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1; self.update_page()

    def show_next_page(self):
        max_p = (len(self.image_paths) - 1) // self.items_per_page
        if self.current_page < max_p:
            self.current_page += 1; self.update_page()