import sys
import os
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QProgressBar, QLineEdit, QPushButton, QLabel, QShortcut
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QKeySequence

# Function to load UI files dynamically
def load_ui_file(ui_file, parent=None):
    if hasattr(sys, '_MEIPASS'):
        # Running in a PyInstaller bundle
        ui_path = os.path.join(sys._MEIPASS, 'ui', ui_file)
    else:
        # Running in a normal Python environment
        ui_path = os.path.join(os.path.dirname(__file__), 'ui', ui_file)
    loadUi(ui_path, parent)

# Splash screen section
class SplashWindows(QWidget):
    def __init__(self):
        super(SplashWindows, self).__init__()
        try:
            load_ui_file("adsb_splash.ui", self)
            print("File 'adsb_splash.ui' executed.")
        except FileNotFoundError:
            print("Error: File 'adsb_splash.ui' not found. Program cannot proceed.")
            sys.exit(1)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.progress_bar = self.findChild(QProgressBar, "progressBar_adsbLoading")
        if self.progress_bar is None:
            print("Error: Progress bar not found. Program cannot proceed.")
            sys.exit(1)
        print("Progress bar is found.")
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress_bar)
        self.progress_value = 0
        self.timer.start(25)  # Adjust the interval as needed

    def update_progress_bar(self):
        if self.progress_value >= 100:
            self.timer.stop()
            print("Open 'adsb_login.ui'")
            self.show_login_screen()
        else:
            self.progress_value += 1
            self.progress_bar.setValue(self.progress_value)

    def show_login_screen(self):
        print("Close 'adsb_splash.ui'")
        self.login = LoginWindows()
        self.login.show()
        self.close()

# Login screen section
class LoginWindows(QWidget):
    def __init__(self):
        super(LoginWindows, self).__init__()
        try:
            load_ui_file("adsb_login.ui", self)
        except FileNotFoundError:
            print("Error: UI file 'adsb_login.ui' not found")
            sys.exit(1)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        print("File 'adsb_login.ui' executed.")
        self.setWindowTitle("ADS-B Login")
        self.username_edit = self.findChild(QLineEdit, "lineEdit_userName")
        self.password_edit = self.findChild(QLineEdit, "lineEdit_passWord")
        self.login_button = self.findChild(QPushButton, "pushButton_login")
        self.login_text = self.findChild(QLabel, "label_loginText")
        self.login_button.clicked.connect(self.validate_login)
        self.enter_shortcut = QShortcut(QKeySequence("Return"), self)
        self.enter_shortcut.activated.connect(self.login_button.click)

    def validate_login(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        if username == "ipp123" and password == "adsb123":
            print("Login successful")
            print("Open 'adsb_main.ui'")
            self.show_main_screen()
        else:
            print("Invalid credentials")
            self.login_text.setText("Invalid username or password")
            self.login_text.setStyleSheet("color: red")

    def show_main_screen(self):
        print("Close 'adsb_login.ui'")
        self.main = MainWindows()
        self.main.show()
        self.close()

class MainWindows(QWidget):
    def __init__(self):
        super(MainWindows, self).__init__()
        try:
            load_ui_file("adsb_main.ui", self)
        except FileNotFoundError:
            print("Error: UI file 'adsb_main.ui' not found")
            sys.exit(1)
        print("File 'adsb_main.ui' executed.")
        self.setWindowTitle("SignalPro ADS-B Displayer")
        self.web_adsb = self.findChild(QWebEngineView, "widget_webadsb")
        self.refresh_button = self.findChild(QPushButton, "pushButton_refresh")
        self.web_adsb.setUrl(QtCore.QUrl("https://www.radarbox.com/@-6.42117,106.79664,z9"))
        self.refresh_button.clicked.connect(self.refresh_webview)

    def refresh_webview(self):
        self.web_adsb.reload()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    splash = SplashWindows()
    splash.show()

    sys.exit(app.exec_())
