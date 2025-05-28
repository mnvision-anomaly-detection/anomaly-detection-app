import os
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QLabel,
    QFileDialog, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from ui.result_window import ResultWindow

class MainWindow(QWidget):
    def __init__(self, detector):
        super().__init__()
        self.detector = detector
        self.setWindowTitle("배터리캡 불량품 검출 프로그램")

        # 상태 변수 초기화
        self.selected_path = None
        self.image_files = []
        self.current_index = 0

        # 스타일시트
        self.setStyleSheet("""
            QWidget { background-color: #FFF; font-family: 'Arial'; }
            QPushButton { background-color: #F3B72E; color: white; font-size: 16px; padding: 12px; border-radius: 10px; }
            QPushButton:hover { background-color: #104681; }
            QPushButton:disabled { background-color: #B0BEC5; }
            QLabel { font-size: 14px; color: #333; }
            #file_label { background-color: #FFF; padding: 10px; border: 1px solid #E0E0E0; border-radius: 8px; }
            #image_preview { border: 1px solid #E0E0E0; border-radius: 10px; }
        """)

        # 레이아웃 구성
        layout = QVBoxLayout(self)
        # 제목
        title = QLabel("🔍 불량품 검출")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 파일 라벨
        self.file_label = QLabel("선택된 경로 없음")
        self.file_label.setObjectName("file_label")
        layout.addWidget(self.file_label)

        # 이미지 탐색 레이아웃
        nav = QHBoxLayout()
        self.left_btn = QPushButton("<")
        self.left_btn.clicked.connect(self.show_previous_image)
        self.image_preview = QLabel()
        self.image_preview.setFixedSize(460, 250)
        self.image_preview.setObjectName("image_preview")
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.right_btn = QPushButton(">")
        self.right_btn.clicked.connect(self.show_next_image)
        nav.addWidget(self.left_btn)
        nav.addWidget(self.image_preview)
        nav.addWidget(self.right_btn)
        layout.addLayout(nav)

        # 선택 버튼 레이아웃
        btn_box = QHBoxLayout()
        self.sel_file = QPushButton("이미지 파일 선택")
        self.sel_file.clicked.connect(self.load_image_file)
        self.sel_folder = QPushButton("이미지 폴더 선택")
        self.sel_folder.clicked.connect(self.load_image_folder)
        btn_box.addWidget(self.sel_file)
        btn_box.addWidget(self.sel_folder)
        layout.addLayout(btn_box)

        # 검출 및 초기화 버튼
        self.detect_btn = QPushButton("검출하기")
        self.detect_btn.setEnabled(False)
        self.detect_btn.clicked.connect(self.start_detection)
        self.reset_btn = QPushButton("초기화")
        self.reset_btn.clicked.connect(self.reset_ui)
        layout.addWidget(self.detect_btn)
        layout.addWidget(self.reset_btn)

    # 파일 선택
    def load_image_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "이미지 파일 선택", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if path:
            self.selected_path = path
            self.image_files = [path]
            self.current_index = 0
            pixmap = QPixmap(path).scaled(460, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_preview.setPixmap(pixmap)
            self.file_label.setText(f"✅ 선택된 파일: {path}")
            self.detect_btn.setEnabled(True)

    # 폴더 선택
    def load_image_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "이미지 폴더 선택", "")
        if folder:
            self.selected_path = folder
            files = sorted([os.path.join(folder, f) for f in os.listdir(folder)
                            if f.lower().endswith(('.png','.jpg','.jpeg','.bmp'))])
            if not files:
                self.file_label.setText("⚠️ 폴더에 이미지 파일이 없습니다.")
                return
            self.image_files = files
            self.current_index = 0
            self.update_image_preview()
            self.file_label.setText(f"📂 선택된 폴더: {folder}")
            self.detect_btn.setEnabled(True)

    # 이미지 미리보기 업데이트
    def update_image_preview(self):
        path = self.image_files[self.current_index]
        pixmap = QPixmap(path).scaled(460, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_preview.setPixmap(pixmap)

    # 이전 이미지
    def show_previous_image(self):
        if self.image_files:
            self.current_index = (self.current_index - 1) % len(self.image_files)
            self.update_image_preview()

    # 다음 이미지
    def show_next_image(self):
        if self.image_files:
            self.current_index = (self.current_index + 1) % len(self.image_files)
            self.update_image_preview()

    # 검출 실행
    def start_detection(self):
        results = self.detector.detect_batch(self.image_files)
        self.result_window = ResultWindow(self.image_files, results)
        self.result_window.show()

    # UI 초기화
    def reset_ui(self):
        self.selected_path = None
        self.image_files = []
        self.current_index = 0
        self.file_label.setText("선택된 경로 없음")
        self.image_preview.clear()
        self.detect_btn.setEnabled(False)