from PyQt5.QtWidgets import QFileDialog

class DataAcquisition:
    """Clase para manejar el guardado de datos."""
    def __init__(self, serial_handler):
        self.serial_handler = serial_handler
        self.file = None

    def start_acquire_data(self, parent):
        options = QFileDialog.Options()
        # Abre un diálogo para que el usuario elija dónde guardar el archivo
        file_name, _ = QFileDialog.getSaveFileName(parent, "Guardar Archivo", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_name:
            # Si se seleccionó un archivo, lo abre
            self.open_file(file_name)
    """
    def open_file(self, file_name):
        try:
            self.file = open(file_name, 'a')       # Intenta abrir el archivo en modo append
        except IOError as e:                       # Si hay un error, lo imprime y establece el archivo como None
            print(f'Error al abrir el archivo: {file_name}, {e}')
            self.file = None
    """
    def open_file(self, file_name):
        try:
            # Primero abre el archivo en modo de escritura para vaciar su contenido y lo cierra inmediatamente
            open(file_name, 'w').close()
            # Luego abre el archivo en modo append
            self.file = open(file_name, 'a')
        except IOError as e:
            #Agregar label en la interfaz notificando error de apertura
            print(f'Error al abrir el archivo: {file_name}, {e}')
            self.file = None


    def close_file(self):
        """Cierra el archivo si está abierto."""
        if self.file:
            try:
                self.file.close()
                print(f'Archivo cerrado.')
            except IOError as e:
                print(f'Error al cerrar el archivo: {e}')

    def save_data_to_file(self, value):
        """Guarda un valor en el archivo si está abierto."""
        if self.file:
            try:
                self.file.write(f'{value}\n')
            except IOError as e:
                print(f'Error al escribir en el archivo: {e}')
