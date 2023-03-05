import socket
import sys
from PySide6.QtCore import QThread
from PySide6.QtWidgets import QApplication, QDialog, QLineEdit, QTextEdit, QVBoxLayout, QHBoxLayout, QPushButton


class CommunicatorClient(QDialog):
    client_number = 0
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Communicator Client")
        self.setGeometry(300, 300, 400, 300)

        # window to read messages
        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)

        # inserting messages
        self.edit_line = QLineEdit()
        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.edit_line)
        bottom_layout.addWidget(send_button)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

        CommunicatorClient.client_number += 1

        self.socket = None
        self.host = "localhost"
        self.port = 55555
        self.name = 'Client' + str(CommunicatorClient.client_number)

        self.connect_to_server()

    def connect_to_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.socket.connect((self.host, self.port))
        except socket.error as e:
            print(str(e))
            sys.exit()

        self.receive_thread = ReceiveThread(self.socket, self)
        self.receive_thread.start()

    def send_message(self):
        message = self.edit_line.text().encode()
        self.socket.send(message)
        self.text_edit.append(f"Me: {self.edit_line.text()}")
        self.edit_line.clear()


class ReceiveThread(QThread):
    def __init__(self, socket, parent=None):
        super().__init__(parent)
        self.socket = socket

    def run(self):
        while True:
            try:
                message = self.socket.recv(1024).decode()
                self.parent().text_edit.append(message)
            except socket.error:
                break
