import collections
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MplCanvas(FigureCanvas):
    """Canvas para la visualización de gráficos usando matplotlib."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        # Crea una nueva figura con el tamaño y resolución especificados
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)    # Agrega un subplot a la figura
        super(MplCanvas, self).__init__(fig)    # Inicializa el canvas de matplotlib
        self.setParent(parent)  # Configura el widget padre

        # Configura la política de tamaño para que el canvas se expanda en ambas direcciones
        FigureCanvas.setSizePolicy(self, 
                                   QtWidgets.QSizePolicy.Expanding, 
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)   # Actualiza la geometría del canvas

class PlotManager:
    """Gestor de la graficación y actualización de datos en el gráfico."""
    def __init__(self, canvas, max_points=1000):
        self.canvas = canvas
        self.max_points = max_points
        self.data = collections.deque([0]*self.max_points, maxlen=self.max_points)  # Inicializa una cola de datos con ceros
        self.buffer = []
        self.ax = self.canvas.axes
        self.line, = self.ax.plot([], [], lw=2) # Crea una línea vacía en el gráfico
        self.anim = None
        self.setup_plot()

    def setup_plot(self):
        """Configura los parámetros iniciales del gráfico."""
        # Establece los límites de los ejes
        self.ax.set_xlim(0, self.max_points - 1)
        self.ax.set_ylim(0, 512)
        self.init_plot()

    def init_plot(self):
        """Inicializa los datos del gráfico."""
        self.line.set_ydata(self.data)
        self.line.set_xdata(range(len(self.data)))
        return self.line,

    def start_animation(self, update_func):
        """Inicia la animación del gráfico."""
        self.anim = animation.FuncAnimation(
            self.canvas.figure, update_func, fargs=(self.data, self.line, self.buffer, self.max_points),
            init_func=self.init_plot, blit=True, interval=50
            #,save_count=1000
        )

    def stop_animation(self):
        """Detiene la animación del gráfico."""
        if self.anim:
            self.anim.event_source.stop()
            self.anim = None

    def update_plot(self, frame, data, line, buffer, max_points=100):
        """Actualiza los datos del gráfico."""
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
