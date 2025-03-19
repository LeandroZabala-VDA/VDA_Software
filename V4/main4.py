import sys
import serial
import time
import collections
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PyQt5 import QtWidgets
from ui2 import Ui_MainWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

def read_serial_data(serial_port, baud_rate, timeout):
    """
    Configura el puerto serie y retorna el objeto serial.
    
    :param serial_port: El puerto serie al que está conectado el Arduino (por ejemplo, 'COM3' en Windows o '/dev/ttyUSB0' en Linux)
    :param baud_rate: La velocidad en baudios de la comunicación serie
    :param timeout: Tiempo de espera en segundos para la lectura del puerto serie
    :return: Objeto serial configurado
    """
    try:
        ser = serial.Serial(serial_port, baud_rate, timeout=timeout)
        print(f'Conectado al puerto {serial_port} a {baud_rate} baudios.')
        time.sleep(2)  # Esperar a que el Arduino reinicie y comience a enviar datos
        return ser
    except serial.SerialException as e:
        print(f'Error de conexión: {e}')
        return None

def update_plot(frame, ser, data, line, buffer, max_points=100):
    """
    Función de actualización para la animación de matplotlib.
    
    :param frame: Parámetro necesario por FuncAnimation, pero no usado.
    :param ser: Objeto serial desde el cual se leen los datos.
    :param data: Lista donde se almacenan los datos recibidos.
    :param line: Línea de la gráfica que se actualiza.
    :param buffer: Buffer secundario para almacenar los datos temporalmente.
    :param max_points: Número máximo de puntos a mostrar en el gráfico.
    :return: Línea actualizada de la gráfica.
    """
    while ser.in_waiting > 0:
        line_data = ser.readline().decode('utf-8').strip()
        try:
            value = int(line_data)
            buffer.append(value)
            if len(buffer) >= 5:  # Actualizar el gráfico cada 5 datos
                data.extend(buffer)
                if len(data) > max_points:
                    data = data[-max_points:]
                buffer.clear()
                line.set_ydata(data)
                line.set_xdata(range(len(data)))
        except ValueError:
            print(f'Valor no válido recibido: {line_data}')
    
    return line,

def main():
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    # Añadir canvas de matplotlib al QGraphicsView
    canvas = MplCanvas(ui.centralwidget, width=7, height=4, dpi=100)
    layout = QtWidgets.QVBoxLayout(ui.graphicsView)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(canvas)
    MainWindow.show()

    serial_port = 'COM3'  # Cambiar al puerto correspondiente
    baud_rate = 1000000
    timeout = 1  # 1 segundo de espera

    ser = read_serial_data(serial_port, baud_rate, timeout)
    
    if ser is None:
        return

    max_points = 1000
    data = collections.deque([0]*max_points, maxlen=max_points)
    buffer = []

    ax = canvas.axes
    ax.set_xlim(0, max_points - 1)  # Ancho de la ventana de datos
    ax.set_ylim(0, 255)  # Rango de los valores esperados
    line, = ax.plot([], [], lw=2)
    
    def init():
        line.set_ydata(data)
        line.set_xdata(range(len(data)))
        return line,

    ani = animation.FuncAnimation(canvas.figure, update_plot, fargs=(ser, data, line, buffer, max_points), init_func=init, blit=True, interval=50)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
