# main.py
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from result import ResultWindow  # 불러오기!

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("실행 창")
        self.setGeometry(100, 100, 300, 150)

        layout = QVBoxLayout()

        self.run_button = QPushButton("검출 실행")
        self.run_button.clicked.connect(self.show_result)

        layout.addWidget(QLabel("불량품 검출 실행 창"))
        layout.addWidget(self.run_button)

        self.setLayout(layout)

    def show_result(self):
        # 예시 이미지와 텍스트 (여기서 실제 결과 넣으면 됨)
        image_path = "sample.jpg"  # 여기에 이미지 경로
        result_text = "불량품이 감지되었습니다"

        self.result_window = ResultWindow(image_path, result_text)
        self.result_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())