import sys
from PyQt5 import QtWidgets, QtCore
from ui2 import Ui_MainWindow
from serial_handler import SerialHandler
from data_acquisition import DataAcquisition
from plot import MplCanvas, PlotManager
from wsclient import WebSocketClient
import threading

class MainApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.serial_handler = SerialHandler()
        self.data_acquisition = DataAcquisition(self.serial_handler)

        # Configuración del canvas para el gráfico
        self.canvas = MplCanvas(self.centralwidget, width=7, height=4, dpi=100)
        layout = QtWidgets.QVBoxLayout(self.graphicsView)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        self.plot_manager = PlotManager(self.canvas)
        
        
        # Conexión de botones a sus respectivas funciones
        self.btn_Puerto.clicked.connect(self.toggle_port)
        self.btn_Start.clicked.connect(self.toggle_start_stop)
        self.btn_Adquirir.clicked.connect(self.toggle_acquire_data)
        
        # Configuración del temporizador para actualizar la lista de puertos
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_ports)
        self.timer.start(1000)
        self.update_ports()

        # Establece un baudrate de 1M baudios por defecto
        self.TextEdit_BaudRate.setPlainText("1000000")
        
        # Se inicializa en modo de NO grabación en archivo
        self.acquiring = False

        # Inicializar la maquina de estados en "Puerto Cerrado"
        self.update_ui_state("Puerto Cerrado")

        self.websocket_client = WebSocketClient("ws://vdamanager.com:8765")

    # Maquina de estados
    def update_ui_state(self, state):
        if state == "Puerto Cerrado":
            self.btn_Puerto.setText("Abrir Puerto")
            self.btn_Puerto.setEnabled(True)
            self.btn_Start.setEnabled(False)
            self.btn_Adquirir.setEnabled(False)
        elif state == "Puerto Abierto":
            self.btn_Puerto.setText("Cerrar Puerto")
            self.btn_Start.setText("Start")
            self.btn_Puerto.setEnabled(True)
            self.btn_Start.setEnabled(True)
            self.btn_Adquirir.setEnabled(False)
        elif state == "Graficando":
            self.btn_Start.setText("Stop")
            self.btn_Puerto.setEnabled(False)
            self.btn_Start.setEnabled(True)
            self.btn_Adquirir.setEnabled(True)
        elif state == "Adquiriendo":
            self.btn_Start.setText("Stop")
            self.btn_Puerto.setEnabled(False)
            self.btn_Start.setEnabled(False)
            self.btn_Adquirir.setEnabled(True)

    def toggle_port(self):
        # Abre o cierra el puerto serial
        if self.serial_handler.is_port_open():
            # Cierra el puerto
            self.serial_handler.close_serial_port()
            self.update_ui_state("Puerto Cerrado")
            self.timer.start(1000)
        else:
            # Abre el puerto
            port = self.CombBox_Port.currentText()
            baud_rate = int(self.TextEdit_BaudRate.toPlainText())
            if self.serial_handler.open_serial_port(port, baud_rate):
                self.update_ui_state("Puerto Abierto")
                self.timer.stop()

    def update_ports(self):
        # Actualiza la lista de puertos disponibles en el ComboBox
        ports = self.serial_handler.get_available_ports()
        current_text = self.CombBox_Port.currentText()
        self.CombBox_Port.clear()
        self.CombBox_Port.addItems(ports)
        if current_text in ports:
            self.CombBox_Port.setCurrentText(current_text)

    def toggle_start_stop(self):
        # Inicia o detiene la graficación de datos - Actualiza la máquina de estados
        if self.serial_handler.is_port_open():
            if self.plot_manager.anim:
                self.stop_plotting()
                self.update_ui_state("Puerto Abierto")
            else:
                self.start_plotting()
                self.update_ui_state("Graficando")

    def start_plotting(self):
        # Inicia la graficación de datos - Actualiza la máquina de estados
        self.serial_handler.send_data("START")
        self.plot_manager.start_animation(self.update_plot)

    def stop_plotting(self):
        # Detiene la graficación de datos - Actualiza la máquina de estados
        self.serial_handler.send_data("STOP")
        self.plot_manager.stop_animation()
        self.statusbar.showMessage('Adquisición detenida.')

    def closeEvent(self, event):
        self.serial_handler.close_serial_port()
        if self.acquiring:
            self.data_acquisition.close_file()
        event.accept()

    def update_plot(self, frame, data, line, buffer, max_points=100):
        # Actualiza el gráfico con los nuevos datos recibidos
        ser = self.serial_handler.serial_port
        while ser.in_waiting > 0:
            line_data = ser.readline().decode('utf-8').strip()
            try:
                value = int(line_data)
                buffer.append(value)
                if self.acquiring:
                    self.data_acquisition.save_data_to_file(value)
                    self.websocket_client.send_message(self.websocket_client,str(value))  # Enviar el valor por WebSocket
                if len(buffer) >= 5:
                    data.extend(buffer)
                    buffer.clear()
                    line.set_ydata(list(data))
                    line.set_xdata(range(len(data)))
            except ValueError:
                # No se porqué caigo aca!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                print(f'Valor no válido recibido: {line_data}')     
        return line,

    def toggle_acquire_data(self):
        # Inicia o detiene la adquisición de datos a un archivo - Actualiza la máquina de estados
        if self.acquiring:
            self.acquiring = False
            self.btn_Adquirir.setText("Adquirir")
            self.update_ui_state("Graficando")
            self.data_acquisition.close_file()
        else:
            self.acquiring = True
            thread = threading.Thread(target=start_websocket_client, args=(self.websocket_client,), daemon=True)
            thread.start()
            
            self.data_acquisition.start_acquire_data(self)
            self.update_ui_state("Adquiriendo")
            self.btn_Adquirir.setText("Detener Adquisición")
            #self.websocket_client.start()
            
def start_websocket_client(websocket_client):
    websocket_client.start()


def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
