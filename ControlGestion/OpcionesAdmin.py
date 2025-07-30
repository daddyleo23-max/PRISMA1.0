import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QDialog, QListWidget, QMessageBox, QApplication, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, QTimer, QDateTime
from RegistroMasivoHuellas import RegistroMasivoHuellas # Asegúrate de que este import sea correcto

class OpcionesAdmin(QWidget):
    def __init__(self, parent=None, salir_callback=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(36)

        lbl = QLabel("Opciones administrativas disponibles:")
        lbl.setStyleSheet("font-size: 32px; color: #00e1ff; font-weight: bold;")
        layout.addWidget(lbl)

        btn_registrar = QPushButton("Registrar alumnos/huellas")
        btn_registrar.setStyleSheet("font-size: 26px; padding: 18px;")
        btn_registrar.clicked.connect(self.abrir_registro_masivo_huellas)
        layout.addWidget(btn_registrar)

        btn_configurar = QPushButton("Configurar salones")
        btn_configurar.setStyleSheet("font-size: 26px; padding: 18px;")
        layout.addWidget(btn_configurar)

        btn_salir = QPushButton("Salir del modo admin")
        btn_salir.setStyleSheet("font-size: 22px; padding: 14px;")
        if salir_callback:
            btn_salir.clicked.connect(salir_callback)
        layout.addWidget(btn_salir)

    def abrir_registro_masivo_huellas(self):
        """
        Abre el diálogo de RegistroMasivoHuellas.
        """
        # Oculta la ventana de opciones de admin antes de abrir el diálogo
        self.hide() 
        self._registro_huellas = RegistroMasivoHuellas(parent=self) 
        # Usar .exec() para QDialogs, esto bloquea la interacción con la ventana padre
        # hasta que el diálogo se cierra.
        self._registro_huellas.exec() 
        # Una vez que el diálogo se cierra, muestra de nuevo la ventana de opciones de admin
        self.show()

