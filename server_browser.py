import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


class ServerBrowser(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Set the window title and size
        self.setWindowTitle("SCUM Browser")
        self.setFixedSize(800, 600)

        # Set the application stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2C3539;
            }

            QMenuBar {
                background-color: #18181a;
                color: white;
            }

            QMenuBar::item {
                background-color: #18181a;
                color: white;
            }

            QMenu {
                background-color: #18181a;
                color: white;
            }

            QMenu::item {
                background-color: #18181a;
                color: white;
            }

            QLabel {
                color: white;
            }

            QComboBox {
                color: black;
                background-color: white;
            }

            QTableWidget {
                color: white;
                background-color: #3A3F3F;
                alternate-background-color: #2C3539;
                selection-color: white;
                selection-background-color: #4F5B66;
            }

            QHeaderView::section {
                background-color: #2C3539;
                color: white;
            }

            QCheckBox {
                color: white;
            }

            QProgressBar {
                color: white;
                background-color: #3A3F3F;
            }

            QToolBar {
                background-color: #18181a;
                color: white;
                border: none;
            }

            QToolButton {
                background-color: #18181a;
                color: white;
                border: none;
            }

            QToolButton:hover {
                background-color: #2C3539;
            }

            QStatusBar {
                background-color: #18181a;
                color: white;
            }
            
            QProgressBar {
                border: none;
                text-align: center;
                background-color: #3A3F3F;
            }

            QProgressBar::chunk {
                background-color: #2ecc71;
                border-radius: 5px;
            }

            QProgressBar::chunk:indeterminate {
                border-radius: 5px;
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2ecc71, stop:1 #27ae60);
                animation: pulse 2s ease-in-out infinite;
            }

            @keyframes pulse {
                0% {
                    border-color: #2ecc71;
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2ecc71, stop:1 #27ae60);
                    opacity: 0.5;
                }
                50% {
                    border-color: #27ae60;
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #27ae60, stop:1 #2ecc71);
                    opacity: 0.75;
                }
                100% {
                    border-color: #2ecc71;
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2ecc71, stop:1 #27ae60);
                    opacity: 0.5;
                }
            }

        """)


        # Create the central widget and layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)

        # Create the title label and player count label
        title_label = QtWidgets.QLabel("SCUMLauncher")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_font = QtGui.QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)

        # Create the filter and sort widgets
        language_label = QtWidgets.QLabel("Language:")
        self.language_combo = QtWidgets.QComboBox()
        self.language_combo.addItems(['English', 'German', 'French', 'Spanish', 'Italian'])
        filters_label = QtWidgets.QLabel("Filters:")
        self.filter_checkboxes = [QtWidgets.QCheckBox("Has Players"), QtWidgets.QCheckBox("PVP"), QtWidgets.QCheckBox("PVE"), QtWidgets.QCheckBox("PvPvE"), QtWidgets.QCheckBox("NO Mechs"), QtWidgets.QCheckBox("Discord Server"), QtWidgets.QCheckBox("Password Protected")]

        # Create the player count label
        self.player_count_label = QtWidgets.QLabel()

        # Create the server list table
        self.table = QtWidgets.QTableWidget()

        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Server Name", "Players", "Map", "Language", "Uptime", "Ping"])

        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # Create the loading spinner
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 0)

        # Add the progress bar to the layout
        layout.addWidget(self.progress_bar)


        # Add the widgets to the layout
        layout.addWidget(title_label)
        layout.addWidget(self.player_count_label)
        filter_layout = QtWidgets.QHBoxLayout()
        filter_layout.addWidget(language_label)
        filter_layout.addWidget(self.language_combo)
        filter_layout.addWidget(filters_label)
        for checkbox in self.filter_checkboxes:
            filter_layout.addWidget(checkbox)
        layout.addLayout(filter_layout)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.table)
        layout.addWidget(self.player_count_label)
        layout.addWidget

        layout.addWidget(self.table)
        
    def start_loading(self):
        self.progress_bar.show()
        self.table.hide()

        # Start a new thread to load the server list
        self.loading_thread = QtCore.QThread()
        self.loading_worker = ServerListLoader()
        self.loading_worker.moveToThread(self.loading_thread)

        # Connect signals to the worker
        self.loading_worker.finished.connect(self.loading_thread.quit)
        self.loading_worker.finished.connect(self.loading_worker.deleteLater)
        self.loading_worker.finished.connect(self.loading_thread.deleteLater)
        self.loading_worker.progress.connect(self.progress_bar.setValue)
        self.loading_worker.finished.connect(self.stop_loading)
        self.loading_worker.error.connect(self.show_loading_error)
        self.loading_worker.add_server.connect(self.add_server_to_table)

        # Start the thread
        self.loading_thread.started.connect(self.loading_worker.load_server_list)
        self.loading_thread.start()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    server_browser = ServerBrowser()
    server_browser.show()
    sys.exit(app.exec_())
