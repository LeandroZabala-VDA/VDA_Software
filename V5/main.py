import sys
import collections
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PyQt5 import QtWidgets, QtCore
from ui2 import Ui_MainWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from serial_handler import SerialHandler
from data_acquisition import DataAcquisition

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

class MainApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.serial_handler = SerialHandler()
        self.data_acquisition = DataAcquisition(self.serial_handler)

        self.canvas = MplCanvas(self.centralwidget, width=7, height=4, dpi=100)
        layout = QtWidgets.QVBoxLayout(self.graphicsView)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

        self.max_points = 1000
        self.data = collections.deque([0]*self.max_points, maxlen=self.max_points)
        self.buffer = []

        self.btn_Puerto.clicked.connect(self.toggle_port)
        self.btn_Start.clicked.connect(self.toggle_start_stop)
        self.btn_Adquirir.clicked.connect(self.acquire_data)

        self.ax = self.canvas.axes
        self.ax.set_xlim(0, self.max_points - 1)
        self.ax.set_ylim(0, 255)
        self.line, = self.ax.plot([], [], lw=2)

        self.anim = None

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_ports)
        self.timer.start(1000)
        self.update_ports()

        self.TextEdit_BaudRate.setPlainText("1000000")

    def toggle_port(self):
        if self.serial_handler.is_port_open():
            self.serial_handler.close_serial_port()
            self.btn_Puerto.setText("Abrir Puerto")
            self.timer.start(1000)
        else:
            port = self.CombBox_Port.currentText()
            baud_rate = int(self.TextEdit_BaudRate.toPlainText())
            if self.serial_handler.open_serial_port(port, baud_rate):
                self.btn_Puerto.setText("Cerrar Puerto")
                self.timer.stop()

    def update_ports(self):
        ports = self.serial_handler.get_available_ports()
        current_text = self.CombBox_Port.currentText()
        self.CombBox_Port.clear()
        self.CombBox_Port.addItems(ports)
        if current_text in ports:
            self.CombBox_Port.setCurrentText(current_text)

    def toggle_start_stop(self):
        if self.serial_handler.is_port_open():
            if self.anim:
                self.stop_acquisition()
            else:
                self.start_acquisition()

    def start_acquisition(self):
        self.serial_handler.send_data("START")
        self.btn_Start.setText("Stop")
        self.anim = animation.FuncAnimation(
            self.canvas.figure, self.update_plot, fargs=(self.data, self.line, self.buffer, self.max_points),
            init_func=self.init_plot, blit=True, interval=50
        )

    def stop_acquisition(self):
        self.serial_handler.send_data("STOP")
        self.btn_Start.setText("Start")
        if self.anim:
            self.anim.event_source.stop()
            self.anim = None
            self.statusbar.showMessage('Adquisición detenida.')

    def closeEvent(self, event):
        self.serial_handler.close_serial_port()
        event.accept()

    def update_plot(self, frame, data, line, buffer, max_points=100):
        ser = self.serial_handler.serial_port
        while ser.in_waiting > 0:
            line_data = ser.readline().decode('utf-8').strip()
            try:
                value = int(line_data)
                buffer.append(value)
                if len(buffer) >= 5:
                    data.extend(buffer)
                    buffer.clear()
                    line.set_ydata(list(data))
                    line.set_xdata(range(len(data)))
            except ValueError:
                print(f'Valor no válido recibido: {line_data}')
        return line,

    def init_plot(self):
        self.line.set_ydata(self.data)
        self.line.set_xdata(range(len(self.data)))
        return self.line,

    def acquire_data(self):
        self.data_acquisition.acquire_data(self)

def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
