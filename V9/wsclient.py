import websocket
from PyQt5.QtCore import QThread, pyqtSignal

class WebSocketClient:
    def __init__(self, url):
        self.url = url
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(self.url,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        

    def send_message(self,ws,message):
        self.ws.send(message)
        print(f"Sent: {message}")
    
    def on_message(self, ws, message):
        print(f"Received from server: {message}")

    def on_error(self, ws, error):
        print(f"Error: {error}")

    def on_close(self, ws):
        print("Disconnected from the server")

    def on_open(self, ws):
        print("Connected to the server")

    
    def start(self):
        self.ws.run_forever()


class WebSocketClientThread(QThread):
    update_signal = pyqtSignal(str)

    def __init__(self, websocket_client):
        super().__init__()
        self.websocket_client = websocket_client

    def run(self):
        self.websocket_client.start()

    def send_update(self, message):
        self.update_signal.emit(message)

