import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog,
    QSpacerItem, QSizePolicy, QHBoxLayout
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from result import ResultWindow


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("배터리캡 불량품 검출 프로그램")
        self.setGeometry(300, 200, 600, 500)

        self.selected_file_path = None
        self.selected_folder_path = None
        self.image_files = []
        self.current_image_index = 0

        self.setStyleSheet("""
            QWidget {
                background-color: #FFF;
                font-family: 'Arial', sans-serif;
            }
            QPushButton {
                background-color: #F3B72E;
                color: white;
                font-size: 16px;
                padding: 12px 24px;
                border-radius: 10px;
                border: none;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                transition: background-color 0.3s, transform 0.2s;
            }
            QPushButton:hover {
                background-color: #104681;
                transform: translateY(-2px);
            }
            QPushButton:disabled {
                background-color: #B0BEC5;
                color: #F5F5F5;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            #title_label {
                font-size: 24px;
                font-weight: bold;
                color: #333;
                padding: 20px;
                margin-bottom: 20px;
            }
            #file_label {
                background-color: #FFFFFF;
                padding: 10px;
                border-radius: 8px;
                margin-bottom: 20px;
                color: #4F4F4F;
                border: 1px solid #E0E0E0;
                text-align: center;
            }
            #image_preview {
                border: 1px solid #E0E0E0;
                padding: 15px;
                margin-bottom: 20px;
                border-radius: 10px;
                background-color: #FFFFFF;
                text-align: center;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        title_label = QLabel("🔍 불량품 검출")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignCenter)

        self.file_label = QLabel("선택된 경로 없음")
        self.file_label.setObjectName("file_label")

        preview_layout = QHBoxLayout()
        self.left_button = QPushButton("<")
        self.left_button.setFixedWidth(40)
        self.left_button.clicked.connect(self.show_previous_image)
        preview_layout.addWidget(self.left_button)

        self.image_preview = QLabel()
        self.image_preview.setObjectName("image_preview")
        self.image_preview.setFixedSize(460, 250)
        self.image_preview.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(self.image_preview)

        self.right_button = QPushButton(">")
        self.right_button.setFixedWidth(40)
        self.right_button.clicked.connect(self.show_next_image)
        preview_layout.addWidget(self.right_button)

        self.select_file_button = QPushButton("이미지 파일 선택")
        self.select_file_button.clicked.connect(self.load_image_file)

        self.select_folder_button = QPushButton("이미지 폴더 선택")
        self.select_folder_button.clicked.connect(self.load_image_folder)

        self.detect_button = QPushButton("검출하기")
        self.detect_button.setEnabled(False)
        self.detect_button.clicked.connect(self.start_detection)

        self.reset_button = QPushButton("초기화")
        self.reset_button.clicked.connect(self.reset_ui)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.select_file_button)
        button_layout.addWidget(self.select_folder_button)

        layout.addWidget(title_label)
        layout.addWidget(self.file_label)
        layout.addLayout(preview_layout)
        layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addLayout(button_layout)
        layout.addWidget(self.detect_button)
        layout.addWidget(self.reset_button)
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(layout)

    def load_image_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "이미지 파일 선택", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.selected_file_path = file_path
            self.file_label.setText(f"✅ 선택된 파일: {file_path}")
            pixmap = QPixmap(file_path).scaled(400, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_preview.setPixmap(pixmap)
            self.detect_button.setEnabled(True)
            self.image_files = []

    def load_image_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "이미지 폴더 선택", "")
        if folder_path:
            self.selected_folder_path = folder_path
            self.file_label.setText(f"📂 선택된 폴더: {folder_path}")
            self.image_preview.clear()
            self.detect_button.setEnabled(True)

            self.image_files = sorted([
                os.path.join(folder_path, f)
                for f in os.listdir(folder_path)
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))
            ])
            if not self.image_files:
                self.file_label.setText("⚠️ 폴더에 이미지 파일이 없습니다.")
                self.detect_button.setEnabled(False)
                return

            self.current_image_index = 0
            self.update_image_preview()

    def update_image_preview(self):
        if self.image_files:
            path = self.image_files[self.current_image_index]
            pixmap = QPixmap(path).scaled(400, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_preview.setPixmap(pixmap)

    def show_previous_image(self):
        if self.image_files:
            self.current_image_index = (self.current_image_index - 1) % len(self.image_files)
            self.update_image_preview()

    def show_next_image(self):
        if self.image_files:
            self.current_image_index = (self.current_image_index + 1) % len(self.image_files)
            self.update_image_preview()

    def start_detection(self):
        if self.selected_file_path:
            self.file_label.setText("🔄 검증 중입니다...")
            self.repaint()
            QTimer.singleShot(1000, self.show_single_result)
        elif self.selected_folder_path:
            self.file_label.setText("🔄 폴더 검증 중입니다...")
            self.repaint()
            QTimer.singleShot(1000, self.show_folder_result)

    def show_single_result(self):
        self.file_label.setText(f"✅ 검출 완료: {self.selected_file_path}")
        self.result_window = ResultWindow(self.selected_file_path)
        self.result_window.show()

    def show_folder_result(self):
        self.file_label.setText(f"📂 폴더 검출 완료: {self.selected_folder_path}")
        self.result_window = ResultWindow(self.image_files)
        self.result_window.show()

    def reset_ui(self):
        self.selected_file_path = None
        self.selected_folder_path = None
        self.image_files = []
        self.current_image_index = 0
        self.file_label.setText("선택된 경로 없음")
        self.image_preview.clear()
        self.detect_button.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

