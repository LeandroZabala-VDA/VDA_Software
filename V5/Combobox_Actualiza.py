import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox
from PyQt5.QtCore import QTimer
from serial.tools import list_ports

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Puertos COM disponibles')
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.comboBox = QComboBox()
        self.comboBox.setEditable(False)
        layout.addWidget(self.comboBox)

        self.setLayout(layout)

        # Creamos un temporizador para actualizar la lista de puertos COM cada segundo
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateComboBoxItems)
        self.timer.start(1000)  # Actualiza cada segundo (1000 ms)

        # Llamamos a updateComboBoxItems inicialmente para llenar la lista al inicio
        self.updateComboBoxItems()

    def updateComboBoxItems(self):
        current_text = self.comboBox.currentText()  # Guardamos el texto actual seleccionado
        current_index = self.comboBox.currentIndex()  # Guardamos el índice actual seleccionado

        self.comboBox.clear()
        ports = [port.device for port in list_ports.comports()]
        self.comboBox.addItems(ports)

        # Restauramos la selección anterior si es posible
        if current_text in ports:
            self.comboBox.setCurrentText(current_text)
        elif current_index < len(ports):
            self.comboBox.setCurrentIndex(current_index)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
