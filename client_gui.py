import os
import re
import socket
import threading
import sys

import qdarkstyle
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QApplication, QGridLayout, QWidget, QListWidget, QPushButton, QLineEdit, QPlainTextEdit


class chat_window(QWidget):

    def mousePressEvent(self, event):
        self.offset = event.pos()

    def mouseMoveEvent(self, event):
        x = event.globalX()
        y = event.globalY()
        x_w = self.offset.x()
        y_w = self.offset.y()
        self.move(x - x_w, y - y_w)

    def __init__(self, parent=None):
        super(chat_window, self).__init__(parent)
        self.setWindowTitle('Crypt v1')
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setGeometry(100, 100, 800, 500)
        self.listFile = QListWidget()
        self.sendBtn = QPushButton('Send')
        self.sendBtn.setDisabled(True)
        self.discBtn = QPushButton('Disconnect')
        self.discBtn.setDisabled(True)
        self.textbox = QLineEdit('')
        self.label = QPlainTextEdit('')
        self.label.setReadOnly(True)
        self.ip_bar = QLineEdit('IP')
        self.q_btn = QPushButton('Exit')
        self.connBtn = QPushButton('Connect')
        self.host = QPushButton('Host')
        self.name_bar = QLineEdit('Name')
        self.repeat = 0
        self.coding = 1
        self.coded = ''

        self.client = Client()

        layout = QGridLayout()

        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_state)

        layout.addWidget(self.sendBtn, 4, 7, 1, 1)
        layout.addWidget(self.discBtn, 1, 6, 1, 1)
        layout.addWidget(self.textbox, 4, 0, 1, 4)
        layout.addWidget(self.label, 3, 0, 1, 0)
        layout.addWidget(self.ip_bar, 1, 2, 1, 1)
        layout.addWidget(self.q_btn, 1, 7, 1, 1)
        layout.addWidget(self.connBtn, 1, 5, 1, 1)
        # layout.addWidget(self.host, 1, 0, 1, 1)
        layout.addWidget(self.name_bar, 1, 1, 1, 1)

        self.host.clicked.connect(self.startServer)
        self.connBtn.clicked.connect(self.connect)
        self.sendBtn.clicked.connect(self.send_msg)
        self.discBtn.clicked.connect(self.disconnect)
        self.q_btn.clicked.connect(self.exit)
        self.setLayout(layout)

    def disconnect(self):
        self.client.disconnect()
        self.sendBtn.setDisabled(True)
        self.connBtn.setDisabled(False)
        self.discBtn.setDisabled(True)
        self.name_bar.setDisabled(False)
        self.ip_bar.setDisabled(False)

    def send_msg(self):
        message = self.textbox.text()
        name = self.name_bar.text()
        self.client.send_msg_manual(name + ": " + message)
        self.textbox.setText("")

    def exit(self):
        os._exit(1)

    def is_ip(self, ip):
        return re.match(r'^\d{1,255}[.]\d{1,255}[.]\d{1,255}[.]\d{1,255}$', ip)

    def connect(self):
        try:
            ip = self.ip_bar.text()
            if self.is_ip(ip) is None:
                text = self.label.toPlainText()
                text += "Invalid IP.\n"
                self.label.setPlainText(text)
            else:
                self.start_timer()
                self.client.connect(ip)
                self.sendBtn.setDisabled(False)
                self.connBtn.setDisabled(True)
                self.discBtn.setDisabled(False)
                self.name_bar.setDisabled(True)
                self.ip_bar.setDisabled(True)

        except (ConnectionRefusedError, TimeoutError):
            text = self.label.toPlainText()
            text += "No Connection found.\n"
            self.label.setPlainText(text)

    def startServer(self):
        self.connBtn.setDisabled(True)
        self.sendBtn.setDisabled(True)
        self.host.setDisabled(True)

    def refresh_state(self):

        if self.client.log != self.label.toPlainText():
            self.label.setPlainText(self.client.log)

    def start_timer(self):
        self.timer.start(140)


class Client:
    def __init__(self):
        self.terminal = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.log = ""

    def connect(self, address):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((address, 10000))
        self.log += "Connected." + "\n"
        print("Connected.")

        oThread = threading.Thread(target=self.get_msg)
        oThread.daemon = True
        oThread.start()

        if self.terminal:
            while True:
                self.sock.send(bytes(input(""), 'utf-8'))
                print("\033")

    def disconnect(self):
        self.sock.close()

    def get_msg(self):
        try:
            while True:
                data = self.sock.recv(1024)
                if not data:
                    break
                print(str(data, 'utf-8'))
                self.log += str(data, 'utf-8') + "\n"
        except ConnectionAbortedError:
            self.log += "Disconnected." + "\n"

    def send_msg_manual(self, message):
        self.sock.send(bytes(message, 'utf-8'))


if __name__ == '__main__':
    if '-s' not in sys.argv:
        app = QApplication(sys.argv)
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        window = chat_window()
        window.show()
        app.exec()
    else:
        try:
            client = Client()
            client.terminal = True
            client.connect(sys.argv[len(sys.argv) - 1])
        except ConnectionRefusedError:
            print("Failed to connect.")
