from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QDialog, QMessageBox
)
from PyQt6.QtCore import Qt
import json
import os

class ClasesRegistradas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget {
                background-color: #23272f;
                border-radius: 18px;
            }
            QLabel#titulo {
                color: #00e1ff;
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 18px;
            }
            QLabel {
                color: #A3BE8C;
                font-size: 20px;
                font-weight: bold;
            }
            QTableWidget {
                background-color: #3B4252;
                border: 1px solid #4C566A;
                border-radius: 8px;
                font-size: 18px;
                color: #ECEFF4;
            }
            QHeaderView::section {
                background-color: #4C566A;
                color: #00e1ff;
                font-size: 18px;
                font-weight: bold;
                padding: 8px;
                border: none;
            }
            QPushButton {
                background-color: #00e1ff;
                color: #1e2229;
                font-size: 18px;
                border-radius: 12px;
                font-weight: bold;
                padding: 10px 0;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #00b3cc;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(24)

        lbl_titulo = QLabel("👜 Clases Registradas")
        lbl_titulo.setObjectName("titulo")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_titulo)

        # Tabla de clases registradas
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Materia", "Grupo", "Horario", "Ver Alumnos"])
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.horizontalHeader().setMinimumSectionSize(120)
        layout.addWidget(self.tabla, stretch=1)

        self.cargar_clases()

    def cargar_clases(self):
        self.tabla.setRowCount(0)
        clases = []
        if os.path.exists("clases.json"):
            with open("clases.json", "r", encoding="utf-8") as file:
                try:
                    clases = json.load(file)
                except json.JSONDecodeError:
                    QMessageBox.critical(self, "Error", "El archivo clases.json tiene un formato inválido.")
                    return
        for row, clase in enumerate(clases):
            self.tabla.insertRow(row)
            self.tabla.setItem(row, 0, QTableWidgetItem(clase.get("materia", "Sin materia")))
            self.tabla.setItem(row, 1, QTableWidgetItem(clase.get("grupo", "Sin grupo")))
            # Asegúrate de que el formato del horario sea el esperado
            horario_str = f"{clase.get('hora_inicio', 'N/A')}-{clase.get('hora_fin', 'N/A')}"
            self.tabla.setItem(row, 2, QTableWidgetItem(horario_str))

            btn_ver_alumnos = QPushButton("Ver Alumnos")
            # MODIFICADO: Construir el nombre completo de la clase para que coincida con alumnos.json
            nombre_clase_completo = (
                f"{clase.get('materia', '')} - {clase.get('grupo', '')} "
                f"({clase.get('docente', '')})"
            ).strip() # .strip() para limpiar espacios extra si alguna parte está vacía

            # Usar lambda con default argument para capturar el valor de nombre_clase_completo
            btn_ver_alumnos.clicked.connect(lambda _, nc=nombre_clase_completo: self.mostrar_alumnos_de_clase(nc))
            self.tabla.setCellWidget(row, 3, btn_ver_alumnos)

    def mostrar_alumnos_de_clase(self, nombre_clase):
        alumnos_en_clase = []
        if os.path.exists("alumnos.json"):
            with open("alumnos.json", "r", encoding="utf-8") as f:
                try:
                    alumnos = json.load(f)
                    for alumno in alumnos:
                        # La lógica de filtrado es correcta aquí, asumiendo que nombre_clase ahora es el formato completo
                        if "clases" in alumno and nombre_clase in alumno["clases"]:
                            alumnos_en_clase.append(alumno)
                except json.JSONDecodeError:
                    QMessageBox.warning(self, "Error de Archivo", "El archivo alumnos.json está dañado o vacío.")
                    alumnos = []
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Alumnos en {nombre_clase}")
        dialog.setMinimumSize(1000, 500)
        layout = QVBoxLayout(dialog)

        if not alumnos_en_clase:
            lbl_no_alumnos = QLabel(f"No hay alumnos inscritos en la clase: {nombre_clase}.")
            lbl_no_alumnos.setStyleSheet("color: #ff4d4d; font-size: 20px; font-weight: bold; padding: 20px;")
            lbl_no_alumnos.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(lbl_no_alumnos)
        else:
            tabla = QTableWidget()
            tabla.setColumnCount(4)
            tabla.setHorizontalHeaderLabels(["Nombre", "Carrera", "Núm. Control", "Correo"])
            tabla.setRowCount(len(alumnos_en_clase))
            for row, alumno in enumerate(alumnos_en_clase):
                tabla.setItem(row, 0, QTableWidgetItem(alumno.get("nombre", "")))
                tabla.setItem(row, 1, QTableWidgetItem(alumno.get("carrera", "")))
                tabla.setItem(row, 2, QTableWidgetItem(alumno.get("numero_control", "")))
                tabla.setItem(row, 3, QTableWidgetItem(alumno.get("correo", "")))
            tabla.resizeColumnsToContents()
            tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            layout.addWidget(tabla)

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(dialog.close)
        layout.addWidget(btn_cerrar)

        dialog.setLayout(layout)
        dialog.exec()