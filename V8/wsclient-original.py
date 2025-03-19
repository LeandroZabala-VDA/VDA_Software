import websocket
import threading

def on_message(ws, message):
    print(f"Received from server: {message}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Disconnected from the server")

def on_open(ws):
    def run(*args):
        print("Connected to the server")
        while True:
            message = input("Enter a message: ")
            ws.send(message)
            print(f"Sent: {message}")

    thread = threading.Thread(target=run)
    thread.start()

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://vdamanager.com:8765",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()
