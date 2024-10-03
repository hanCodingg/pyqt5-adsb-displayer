import sys
import os
import subprocess
import logging
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QProgressBar, QLineEdit, QPushButton, QLabel, QShortcut
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QKeySequence

# Logging function
logging.basicConfig(level=logging.INFO)

# Function to load UI files dynamically
def load_ui_file(ui_file, parent=None):
    if hasattr(sys, '_MEIPASS'):
        ui_path = os.path.join(sys._MEIPASS, 'ui', ui_file)
    else:
        ui_path = os.path.join(os.path.dirname(__file__), 'ui', ui_file)
    loadUi(ui_path, parent)

# Splash screen section
class SplashWindows(QWidget):
    # Loading splash screen ui
    def __init__(self):
        super(SplashWindows, self).__init__()
        try:
            load_ui_file("adsb_splash.ui", self)
            logging.info("File 'adsb_splash.ui' executed.")
        except FileNotFoundError:
            logging.error("Error: File 'adsb_splash.ui' not found. Program cannot proceed.")
            sys.exit(1)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.progress_bar = self.findChild(QProgressBar, "progressBar_adsbLoading")
        
        # Setting timer for progress bar
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress_bar)
        self.progress_value = 0
        self.timer.start(50)  # Adjust the interval as needed
        
        # Running batch file
        self.run_batch_file("run-dump1090-hh.bat")

    # Updating progress bar function
    def update_progress_bar(self):
        if self.progress_value >= 100:
            self.timer.stop()
            logging.info("Open 'adsb_login.ui'")
            self.show_login_screen()
        else:
            self.progress_value += 1
            self.progress_bar.setValue(self.progress_value)
    
    # Running batch file function
    def run_batch_file(self, batch_file):
        try:
            current_directory = os.path.dirname(os.path.abspath(__file__))
            os.chdir(current_directory)
            subprocess.Popen(batch_file, shell=True)
            logging.info(f"Running batch file: {batch_file}")
        except Exception as e:
            logging.error(f"Failed to run batch file: {batch_file}, Error: {e}")
    
    # Showing login screen function
    def show_login_screen(self):
        logging.info("Close 'adsb_splash.ui'")
        self.login = LoginWindows()
        self.login.show()
        self.close()

# Login screen section
class LoginWindows(QWidget):
    # Loading login screen ui
    def __init__(self):
        super(LoginWindows, self).__init__()
        try:
            load_ui_file("adsb_login.ui", self)
        except FileNotFoundError:
            logging.error("Error: UI file 'adsb_login.ui' not found")
            sys.exit(1)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        logging.info("File 'adsb_login.ui' executed.")
        self.setWindowTitle("ADS-B Login")
        self.username_edit = self.findChild(QLineEdit, "lineEdit_userName")
        self.password_edit = self.findChild(QLineEdit, "lineEdit_passWord")
        self.login_button = self.findChild(QPushButton, "pushButton_login")
        self.login_text = self.findChild(QLabel, "label_loginText")
        
        # Setting button and 'enter' key for login function
        self.login_button.clicked.connect(self.validate_login)
        self.enter_shortcut = QShortcut(QKeySequence("Return"), self)
        self.enter_shortcut.activated.connect(self.login_button.click)

    # Validating login function
    def validate_login(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        if username == "ipp123" and password == "adsb123":
            logging.info("Login successful")
            logging.info("Open 'adsb_main.ui'")
            self.show_main_screen()
        else:
            logging.error("Invalid credentials")
            self.login_text.setText("Invalid username or password")
            self.login_text.setStyleSheet("color: red")

    # Showing main screen function
    def show_main_screen(self):
        logging.info("Close 'adsb_login.ui'")
        self.main = MainWindows()
        self.main.show()
        self.close()

# Main screen section
class MainWindows(QWidget):
    # Loading main screen ui
    def __init__(self):
        super(MainWindows, self).__init__()
        try:
            load_ui_file("adsb_main.ui", self)
        except FileNotFoundError:
            logging.error("Error: UI file 'adsb_main.ui' not found")
            sys.exit(1)
        logging.info("File 'adsb_main.ui' executed.")
        self.setWindowTitle("SignalPro ADS-B Displayer")
        self.web_adsb = self.findChild(QWebEngineView, "widget_webadsb")
        self.refresh_button = self.findChild(QPushButton, "pushButton_refresh")
        
        # Setting web URL
        self.web_adsb.setUrl(QtCore.QUrl("http://localhost:8080"))
        
        # Setting refresh button for the website
        self.refresh_button.clicked.connect(self.refresh_webview)

    # Refreshing website
    def refresh_webview(self):
        self.web_adsb.reload()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    splash = SplashWindows()
    splash.show()

    sys.exit(app.exec_())
