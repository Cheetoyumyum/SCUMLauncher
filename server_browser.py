import sys
import requests
import json
from bs4 import BeautifulSoup
from PyQt5 import QtWidgets, QtGui, QtCore
import re


class ServerBrowser(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.update_server_list()

    def init_ui(self):
        # Set the window title and size
        self.setWindowTitle("SCUM Browser")
        self.setFixedSize(800, 600)

        # Set the application stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2C3539;
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
            }

            QHeaderView::section {
                background-color: #2C3539;
                color: white;
            }
        """)

        # Create the central widget and layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)

        # Create the title label and player count label
        title_label = QtWidgets.QLabel("Server Browser")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_font = QtGui.QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)

        # Create the filter and sort widgets
        filter_label = QtWidgets.QLabel("Filter:")
        language_label = QtWidgets.QLabel("Language:")
        password_label = QtWidgets.QLabel("Password Protected:")

        self.language_combo = QtWidgets.QComboBox()
        self.language_combo.addItems(['English', 'German', 'French', 'Spanish', 'Italian'])

        self.password_checkbox = QtWidgets.QCheckBox()

        sort_label = QtWidgets.QLabel("Sort By:")

        self.sort_combo = QtWidgets.QComboBox()
        self.sort_combo.addItems(['Name', 'Players', 'Ping', 'Uptime'])

        # Create the player count label
        self.player_count_label = QtWidgets.QLabel()

        # Create the server list table
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['Name', 'Uptime', 'Last Played', 'Map', 'Players', 'Ping'])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSortingEnabled(True)

        # Add the widgets to the layout
        layout.addWidget(title_label)
        layout.addWidget(self.player_count_label)
        layout.addWidget(filter_label)
        filter_layout = QtWidgets.QHBoxLayout()
        filter_layout.addWidget(language_label)
        filter_layout.addWidget(self.language_combo)
        filter_layout.addWidget(password_label)
        filter_layout.addWidget(self.password_checkbox)
        layout.addLayout(filter_layout)
        layout.addWidget(sort_label)
        layout.addWidget(self.sort_combo)
        layout.addWidget(self.table)

        # Connect the signals and slots
        self.language_combo.currentIndexChanged.connect(self.update_server_list)
        self.password_checkbox.stateChanged.connect(self.update_server_list)
        self.sort_combo.currentIndexChanged.connect(self.update_server_list)
        self.table.horizontalHeader().sectionClicked.connect(self.sort_server_list)

    def get_server_list(self):
        # Fetch the server list from the provided URL using requests library
        url = 'https://www.battlemetrics.com/servers/scum'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        script_tag = soup.find('script', text=re.compile('var\s+servers\s+='))
        
        if script_tag is None:
            print('Script tag not found')
            return []
        
        # Extract the server list from the script tag using regular expressions
        server_list_json = re.search(r'var\s+servers\s+=\s+JSON.parse\(\'(.*)\'\);\s+', str(script_tag.string)).group(1)
        server_list = json.loads(server_list_json)
        
        # Convert the server list to the format expected by the app
        filtered_list = []
        for server in server_list:
            name = server['attributes']['name']
            uptime = server['attributes']['details']['uptime']
            last_played = server['attributes']['details']['lastPlayed']
            map = server['attributes']['details']['map']
            player_count = server['attributes']['details']['playerCount']
            ping = server['attributes']['details']['ping']
            filtered_list.append({'name': name, 'uptime': uptime, 'last_played': last_played, 'map': map, 'player_count': player_count, 'ping': ping})
        
        # Filter by language and password protection
        language = self.language_combo.currentText()
        password_protected = self.password_checkbox.isChecked()
        filtered_list = [server for server in filtered_list if server['name'] != '' and (not language or language == server['language']) and (not password_protected or server['password_protected'])]
        
        return filtered_list



    def sort_server_list(self, server_list):
        # Sort the server list based on the chosen sort key
        sort_key = self.sort_combo.currentText()
        if sort_key == 'Name':
            server_list.sort(key=lambda x: x['name'])
        elif sort_key == 'Players':
            server_list.sort(key=lambda x: x['player_count'])
        elif sort_key == 'Ping':
            server_list.sort(key=lambda x: x['ping'])
        elif sort_key == 'Uptime':
            server_list.sort(key=lambda x: x['uptime'])

        return server_list

    def update_player_count_label(self):
        # Update the player count label with the total player count
        server_list = self.get_server_list()
        total_player_count = sum([int(server['player_count']) for server in server_list])
        self.player_count_label.setText(f"Total Players: {total_player_count}")

    def update_server_list(self):
        # Update the server list table with the filtered and sorted server list
        self.table.clearContents()
        self.table.setRowCount(0)
        server_list = self.get_server_list()
        server_list = self.sort_server_list(server_list)
        for i, server in enumerate(server_list):
            name = server['name']
            uptime = server['uptime']
            last_played = server['last_played']
            map = server['map']
            player_count = server['player_count']
            ping = server['ping']
            self.table.insertRow(i)
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(name))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(uptime))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(last_played))
            self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(map))
            self.table.setItem(i, 4, QtWidgets.QTableWidgetItem(str(player_count)))
            self.table.setItem(i, 5, QtWidgets.QTableWidgetItem(str(ping)))

        self.update_player_count_label()
        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    server_browser = ServerBrowser()
    server_browser.show()
    sys.exit(app.exec_())