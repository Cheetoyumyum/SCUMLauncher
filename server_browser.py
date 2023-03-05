import sys
import requests
from PyQt5 import QtWidgets, QtGui, QtCore
import time
import pypresence


class ServerBrowser(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Set the window title and size
        self.setWindowTitle("SCUMLauncher")
        self.setFixedSize(800, 600)


        # Initialize the Discord Rich Presence client
        self.client_id = '1081709857641615442'
        self.RPC = pypresence.Presence(self.client_id)
        self.RPC.connect()
        # Update the Discord Rich Presence
        try:
            self.RPC.update(
                details="Only the best",
                state="Browsing SCUM Servers",
                large_image="scum",
                large_text="SCUMLauncher",
                small_image="python",
                small_text="Python 3.9.2",
                start=time.time(),
                party_id="party182827",
                party_size=[1, 15],
                join="join123",
                spectate="spectate123",
            )
        except pypresence.exceptions.InvalidPipe:
            pass
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
                border: none;
                text-align: center;
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
        self.language_combo.addItems(['All', 'English', 'German', 'French', 'Spanish', 'Italian'])
        self.language_combo.setCurrentIndex(0) # Set default to All
        filters_label = QtWidgets.QLabel("Filters:")
        self.filter_checkboxes = [QtWidgets.QCheckBox("Has Players"), QtWidgets.QCheckBox("PVP"), QtWidgets.QCheckBox("PVE"), QtWidgets.QCheckBox("PvPvE"), QtWidgets.QCheckBox("NO Mechs"), QtWidgets.QCheckBox("Discord Server"), QtWidgets.QCheckBox("Password Protected")]

        # Create the player count label
        self.player_count_label = QtWidgets.QLabel()

        # Create the server list table
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Server Name", "Players", "Map", "Language", "Uptime", "Ping"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.table.setSelectionMode(QtWidgets.QTableWidget.SingleSelection)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)

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
        layout.addWidget(self.table)

    def start_loading(self):
        self.progress_bar.show()
        self.table.hide()

        # Start a new thread to load the server list
        self.loading_thread = QtCore.QThread()
        self.loading_worker = ServerListLoader(self.language_combo.currentText(), [cb.isChecked() for cb in self.filter_checkboxes], "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbiI6IjUxZjUzN2IzNjA1NjA3NmYiLCJpYXQiOjE2NzgwNDQ4NTAsIm5iZiI6MTY3ODA0NDg1MCwiaXNzIjoiaHR0cHM6Ly93d3cuYmF0dGxlbWV0cmljcy5jb20iLCJzdWIiOiJ1cm46dXNlcjo2NzY0NzkifQ.Wtrr6qLrO_vCC-FCfKx4e9BfYGM_OPUnbOTDUkMf1NQ")
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

    def add_server_to_table(self, server):
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Populate the row with data from the server object
        self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(server.name))
        self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(server.players)))
        self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(server.map))
        self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(server.language))
        self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(server.uptime))
        self.table.setItem(row, 5, QtWidgets.QTableWidgetItem(str(server.ping)))

        # Update the RPC status with the new server information
        self.update_rpc_status(server)


    def stop_loading(self):
        self.progress_bar.hide()
        self.table.show()

    def show_loading_error(self, error_msg):
        QtWidgets.QMessageBox.warning(self, "Error", error_msg)

    def clear_table(self):
        self.table.setRowCount(0)

    def get_selected_server(self):
        selected = self.table.selectedItems()
        if len(selected) > 0:
            row = selected[0].row()
            server_name = self.table.item(row, 0).text()
            server_players = int(self.table.item(row, 1).text())
            server_map = self.table.item(row, 2).text()
            server_language = self.table.item(row, 3).text()
            server_uptime = self.table.item(row, 4).text()
            server_ping = int(self.table.item(row, 5).text())
            return Server(server_name, server_players, server_map, server_language, server_uptime, server_ping)
        else:
            return None


class ServerListLoader(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(int)
    error = QtCore.pyqtSignal(str)
    add_server = QtCore.pyqtSignal(object)

    def __init__(self, language, filters):
        super().__init__()
        self.language = language
        self.filters = filters

    def load_server_list(self):
        try:
            url = "https://api.battlemetrics.com/servers?filter[game]=scum&page[size]=100"
            # Make the request to get the server list
            response = requests.get(url)
            
            if response.status_code == 200:
                server_list = response.json()["data"]
            else:
                self.error.emit("Failed to get server list: " + str(response.status_code))

            if response.status_code != 200:
                raise Exception("Failed to get server list")

            server_list = response.json()["data"]

            # Loop through the servers and add them to the table
            for i, server in enumerate(server_list):
                if not self.passes_filters(server):
                    continue

                # Convert the data into a Server object and emit the signal
                server_object = Server(server["attributes"]["name"],
                                        server["attributes"]["players"],
                                        server["attributes"]["details"]["map"],
                                        server["attributes"]["details"]["language"],
                                        server["attributes"]["details"]["gamedir"],
                                        server["attributes"]["details"]["appid"],
                                        server["attributes"]["details"]["gameport"],
                                        server["attributes"]["details"]["steamid"],
                                        server["attributes"]["details"]["spectator"],
                                        server["attributes"]["details"]["version"],
                                        server["attributes"]["details"]["edf"],
                                        server["attributes"]["details"]["port"],
                                        server["attributes"]["details"]["secure"],
                                        server["attributes"]["details"]["bots"],
                                        server["attributes"]["details"]["dedicated"],
                                        server["attributes"]["details"]["gametags"],
                                        server["id"])
                self.add_server.emit(server_object)

                # Update the progress bar
                self.progress.emit(int(i / len(server_list) * 100))

        except Exception as e:
            self.error.emit(str(e))

        self.progress.emit(100)
        self.finished.emit()

    def passes_filters(self, server):
        if self.language != "All" and server["attributes"]["details"]["language"] != self.language:
            return False
        if self.filters[0] and server["attributes"]["players"] == 0:
            return False
        if self.filters[1] and server["attributes"]["details"]["gametags"].find("pvp") == -1:
            return False
        if self.filters[2] and server["attributes"]["details"]["gametags"].find("pve") == -1:
            return False
        if self.filters[3] and server["attributes"]["details"]["gametags"].find("pvpve") == -1:
            return False
        if self.filters[4] and server["attributes"]["details"]["gametags"].find("nomechs") == -1:
            return False
        if self.filters[5] and server["attributes"]["details"]["gametags"].find("discord") == -1:
            return False
        if self.filters[6] and server["attributes"]["passworded"] == False:
            return False

        return True

class Server:
    def __init__(self, name, players, map_name, language, gamedir, appid, gameport, steamid, spectator, version, edf, port, secure, bots, dedicated, game_tags, gameid):
        self.name = name
        self.players = players
        self.map = map_name
        self.language = language
        self.gamedir = gamedir
        self.appid = appid
        self.gameport = gameport
        self.steamid = steamid
        self.spectator = spectator
        self.version = version
        self.edf = edf
        self.port = port
        self.secure = secure
        self.bots = bots
        self.dedicated = dedicated
        self.game_tags = game_tags
        self.gameid = gameid

        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    server_browser = ServerBrowser()
    server_browser.show()
    sys.exit(app.exec_())

