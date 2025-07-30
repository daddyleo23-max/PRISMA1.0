from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton,
    QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt
import json
import os

class RegistrarDocentes(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget { background-color: #23272f; border-radius: 18px; }
            QLabel#titulo { color: #00e1ff; font-size: 28px; font-weight: bold; margin-bottom: 18px; }
            QLabel { color: #A3BE8C; font-size: 20px; font-weight: bold; }
            QLineEdit, QComboBox {
                background: #2E3440; color: #00e1ff; font-size: 22px;
                border: 2px solid #00e1ff; border-radius: 10px; padding: 12px; margin-bottom: 18px;
            }
            QPushButton {
                background-color: #00e1ff; color: #1e2229; font-size: 22px;
                border-radius: 16px; font-weight: bold; padding: 18px 0; min-width: 220px;
            }
            QPushButton:hover { background-color: #00b3cc; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(24)

        lbl_titulo = QLabel("Registrar Docente")
        lbl_titulo.setObjectName("titulo")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_titulo)

        form = QFormLayout()
        self.input_nombre = QLineEdit()
        self.input_area = QComboBox()
        self.input_area.addItems([
            "Ingeniería en Sistemas Computacionales",
            "Ingeniería Electrónica",
            "Ingeniería Mecatrónica",
            "Ingeniería Industrial",
            "Ingeniería Civil",
            "Ingeniería Química",
            "Ingeniería en Energías Renovables",
            "Ingeniería Biomédica",
            "Ingeniería en Software",
            "Ingeniería en Telecomunicaciones"
        ])
        self.input_placa = QLineEdit()
        self.input_placa.setPlaceholderText("Ejemplo: ISC4501879")
        self.input_correo = QLineEdit()
        self.input_correo.setReadOnly(True)

        # Vincular correo a la placa
        self.input_placa.textChanged.connect(self.actualizar_correo)

        form.addRow("Nombre completo:", self.input_nombre)
        form.addRow("Área:", self.input_area)
        form.addRow("Placa:", self.input_placa)
        form.addRow("Correo Institucional:", self.input_correo)

        layout.addLayout(form)

        btn_huella = QPushButton("Registrar Huella Dactilar")
        btn_huella.clicked.connect(self.registrar_huella)
        layout.addWidget(btn_huella)

        btn_registrar = QPushButton("Registrar Docente")
        btn_registrar.clicked.connect(self.registrar_docente)
        layout.addWidget(btn_registrar)

        layout.addStretch()

        self.huella_asignada = None

    def actualizar_correo(self):
        placa = self.input_placa.text().strip()
        if placa:
            self.input_correo.setText(f"{placa.lower()}@pachuca.tecnm.mx")
        else:
            self.input_correo.clear()

    def registrar_huella(self):
        self.huella_asignada = "huella_simulada"
        QMessageBox.information(self, "Huella", "Huella registrada correctamente (simulado).")

    def registrar_docente(self):
        nombre = self.input_nombre.text().strip()
        area = self.input_area.currentText()
        placa = self.input_placa.text().strip().upper()
        correo = self.input_correo.text().strip()
        if not (nombre and area and placa and correo):
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios.")
            return
        if not self.huella_asignada:
            QMessageBox.warning(self, "Error", "Debes registrar la huella dactilar antes de guardar al docente.")
            return

        docente = {
            'nombre': nombre,
            'area': area,
            'placa': placa,
            'correo': correo,
            'huella': self.huella_asignada
        }

        # Guardar en docentes.json
        docentes = []
        if os.path.exists("docentes.json"):
            with open("docentes.json", "r", encoding="utf-8") as f:
                try:
                    docentes = json.load(f)
                except json.JSONDecodeError:
                    docentes = []
        docentes.append(docente)
        with open("docentes.json", "w", encoding="utf-8") as f:
            json.dump(docentes, f, ensure_ascii=False, indent=2)

        QMessageBox.information(self, "Éxito", f"Docente registrado correctamente.\nPlaca: {placa}\nCorreo: {correo}")
        self.input_nombre.clear()
        self.input_placa.clear()
        self.input_correo.clear()
        self.huella_asignada = None