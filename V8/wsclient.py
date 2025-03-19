import websocket
from PyQt5.QtCore import QThread, pyqtSignal
import threading
import time

class WebSocketClient:
    def __init__(self, url):
        self.url = url
        self.ws = None
        self.thread = None
        self.connected = False
        self.connect()

    def connect(self):
        if self.connected:
            return
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(self.url,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.thread = threading.Thread(target=self.ws.run_forever)
        self.thread.daemon = True
        self.thread.start()
        # Espera a que la conexión esté lista
        conn_timeout = 5
        while not self.ws.sock or not self.ws.sock.connected and conn_timeout:
            time.sleep(1)
            conn_timeout -= 1
        if not conn_timeout:
            print("Unable to connect to the WebSocket server.")
        else:
            self.connected = True

    def send_message(self, message):
        if self.ws.sock and self.ws.sock.connected:
            self.ws.send(message)
            print(f"Sent: {message}")
        else:
            print("WebSocket is not connected. Reconnecting...")
            self.connected = False
            self.connect()

    def on_message(self, ws, message):
        print(f"Received from server: {message}")

    def on_error(self, ws, error):
        print(f"Error: {error}")

    def on_close(self, ws):
        print("Disconnected from the server")
        self.connected = False
        # Try to reconnect
        self.connect()

    def on_open(self, ws):
        print("Connected to the server")

    def start(self):
        self.connect()

class WebSocketClientThread(QThread):
    update_signal = pyqtSignal(str)

    def __init__(self, websocket_client):
        super().__init__()
        self.websocket_client = websocket_client

    def run(self):
        self.websocket_client.start()

    def send_update(self, message):
        self.websocket_client.send_message(message)
