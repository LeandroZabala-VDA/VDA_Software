import serial
from serial.tools import list_ports

class SerialHandler:
    def __init__(self):
        self.serial_port = None

    def get_available_ports(self):
        return [port.device for port in list_ports.comports()]

    def open_serial_port(self, port, baud_rate, timeout=1):
        try:
            self.serial_port = serial.Serial(port, baud_rate, timeout=timeout)
            print(f'Conectado al puerto {port} a {baud_rate} baudios.')
            return True
        except serial.SerialException as e:
            print(f'Error de conexión: {e}')
            return False

    def close_serial_port(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            print('Puerto serie cerrado.')

    def is_port_open(self):
        return self.serial_port and self.serial_port.is_open

    def send_data(self, data):
        if self.is_port_open():
            self.serial_port.write(data.encode())
            print(f'Datos enviados: {data}')
