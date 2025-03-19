from PyQt5.QtWidgets import QFileDialog

class DataAcquisition:
    def __init__(self, serial_handler):
        self.serial_handler = serial_handler

    def acquire_data(self, parent):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(parent, "Guardar Archivo", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_name:
            self.save_data_to_file(file_name)

    def save_data_to_file(self, file_name):
        if self.serial_handler.is_port_open():
            try:
                with open(file_name, 'w') as file:
                    while self.serial_handler.serial_port.in_waiting > 0:
                        line_data = self.serial_handler.serial_port.readline().decode('utf-8').strip()
                        file.write(f"{line_data}\n")
                    print(f'Datos guardados en {file_name}')
            except IOError as e:
                print(f'Error al escribir en el archivo: {e}')
