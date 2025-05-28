import sys
import yaml
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from core.detector import Detector

if __name__ == "__main__":
    with open("configs/config.yaml") as f:
        cfg = yaml.safe_load(f)

    detector = Detector(cfg)
    
    app = QApplication(sys.argv)
    win = MainWindow(detector)
    win.showFullScreen()
    sys.exit(app.exec_())