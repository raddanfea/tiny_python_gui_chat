import os
import socket
import threading


class Server:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []
        self.sock.bind(('0.0.0.0', 10000))
        self.sock.listen(1)

    def handler(self, c, a):
        while True:
            try:
                data = c.recv(1024)
            except Exception:
                print(str(a[0]) + ':' + str(a[1]), "disconnected")
                self.connections.remove(c)
                c.close()
                self.send_all("Someone left.".encode('utf-8'))
                break
            self.send_all(data)

    def send_all(self, data):
        for connection in self.connections:
            connection.send(data)

    def run(self):
        try:
            while True:
                c, a = self.sock.accept()
                self.send_all("Someone joined.".encode('utf-8'))
                cThread = threading.Thread(target=self.handler, args=(c, a))
                cThread.daemon = True
                cThread.start()
                self.connections.append(c)
                print(str(a[0]) + ':' + str(a[1]), "connected")
        except KeyboardInterrupt:
            for each in self.connections:
                each.close()
            self.sock.close()
            os._exit(1)


if __name__ == '__main__':
    server = Server()
    server.run()
