import socket
import sys
from PySide6 import QtGui
from PySide6.QtCore import QThread
from PySide6.QtWidgets import QApplication, QDialog, QLineEdit, QTextEdit, QVBoxLayout, QHBoxLayout, QPushButton, \
    QFileDialog
from PIL import Image
import io


class CommunicatorClient(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Communicator Client")
        self.setGeometry(300, 300, 800, 700)

        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QtGui.QFont("Courier", 9))
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)

        self.edit_line = QLineEdit()
        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message)
        upload_button = QPushButton("Upload Image")
        upload_button.clicked.connect(self.upload_image)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.edit_line)
        bottom_layout.addWidget(send_button)
        bottom_layout.addWidget(upload_button)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

        self.socket = None
        self.host = "localhost"
        self.port = 55555

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

    def upload_image(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Image File", ".", "Images (*.png *.jpg *.jpeg *.bmp)")
        if filename:
            image = Image.open(filename)

            # resize the image
            width, height = image.size
            aspect_ratio = height / width
            new_width = 100
            new_height = aspect_ratio * new_width
            image = image.resize((new_width, int(new_height)))

            image = image.convert('L')

            pixels = image.getdata()

            # replace each pixel with a character from array
            chars = ["B", "S", "#", "&", "@", "$", "%", "*", "!", ":", "."]
            new_pixels = [chars[pixel // 25] for pixel in pixels]
            new_pixels = ''.join(new_pixels)

            # split string of chars into multiple strings of length equal to new width and create a list
            new_pixels_count = len(new_pixels)
            ascii_image = [new_pixels[index:index + new_width] for index in range(0, new_pixels_count, new_width)]
            ascii_image = "\n".join(ascii_image)
            # with open(filename, "rb") as file:
            #     image_data = file.read()
            # ascii_art = self.convert_to_ascii(image_data)
            message = ascii_image.encode()
            self.socket.sendall(message)
            self.text_edit.append("Me: [Image]")

    # def convert_to_ascii(self, img_bytes, width=500):
    #     image = Image.open(io.BytesIO(img_bytes))
    #     w, h = image.size
    #     new_h = int(h * (width / float(w)))
    #     scaled_image = image.resize((width, new_h)).convert('L')
    #
    #     # Define the ASCII characters to represent different shades of gray
    #     ascii_chars = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]
    #
    #     # Convert each pixel to an ASCII character
    #     ascii_pixels = "".join([ascii_chars[pixel // 25] for pixel in scaled_image.getdata()])
    #     ascii_text = "\n".join([ascii_pixels[i:i + width] for i in range(0, len(ascii_pixels), width)])
    #
    #     return ascii_text


class ReceiveThread(QThread):
    def __init__(self, socket, parent=None):
        super().__init__(parent)
        self.socket = socket

    def run(self):
        while True:
            try:
                message = self.socket.recv(2020).decode()
                self.parent().text_edit.append(message)
            except socket.error:
                break
