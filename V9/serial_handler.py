import serial
from serial.tools import list_ports

class SerialHandler:
    """Manejador para la comunicación serial."""
    def __init__(self):
        self.serial_port = None     # Inicializa el puerto serial como None

    def get_available_ports(self):
        """Obtiene una lista de puertos seriales disponibles."""
        return [port.device for port in list_ports.comports()]

    def open_serial_port(self, port, baud_rate, timeout=1):
        """Abre una conexión con el puerto serial especificado."""
        try:
            # Intenta abrir el puerto serial con los parámetros dados
            self.serial_port = serial.Serial(port, baud_rate, timeout=timeout)
            print(f'Conectado al puerto {port} a {baud_rate} baudios.')
            return True
        except serial.SerialException as e:
            # Si hay un error, lo imprime y retorna False
            print(f'Error de conexión: {e}')
            return False

    def close_serial_port(self):
        """Cierra la conexión con el puerto serial si está abierta."""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            print('Puerto serie cerrado.')

    def is_port_open(self):
        """Verifica si el puerto serial está abierto."""
        return self.serial_port and self.serial_port.is_open    # Retorna True si el puerto existe y está abierto

    def send_data(self, data):
        """Envía datos a través del puerto serial si está abierto."""
        if self.is_port_open():
            # Codifica los datos a bytes y los envía
            self.serial_port.write(data.encode())
            print(f'Datos enviados: {data}')

    def clear_buffers(self):
        """Limpia los buffers de entrada y salida del puerto serial."""
        if self.is_port_open():
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()
            print('Buffers de entrada y salida limpiados.')
