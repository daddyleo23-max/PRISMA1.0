from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt
import json
import os

CARRERAS = [
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
]

class ConsultarAlumnos(QWidget):
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
            QLineEdit, QComboBox {
                background: #2E3440;
                color: #00e1ff;
                font-size: 20px;
                border: 2px solid #00e1ff;
                border-radius: 10px;
                padding: 10px;
                margin-bottom: 12px;
            }
            QPushButton {
                background-color: #00e1ff;
                color: #1e2229;
                font-size: 20px;
                border-radius: 14px;
                font-weight: bold;
                padding: 12px 0;
                min-width: 160px;
            }
            QPushButton:hover {
                background-color: #00b3cc;
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
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(18)

        lbl_titulo = QLabel("Consultar Alumnos")
        lbl_titulo.setObjectName("titulo")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_titulo)

        # --- Barra de búsqueda ---
        search_layout = QHBoxLayout()
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar por nombre, apellidos o número de control...")
        btn_buscar = QPushButton("Buscar")
        btn_buscar.clicked.connect(self.buscar_alumnos)
        btn_guardar = QPushButton("Guardar Cambios")
        btn_guardar.clicked.connect(self.guardar_todos_los_cambios)
        search_layout.addWidget(self.input_busqueda)
        search_layout.addWidget(btn_buscar)
        search_layout.addWidget(btn_guardar)
        layout.addLayout(search_layout)

        # --- Tabla de alumnos ---
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels([
            "Nombre(s)", "Carrera", "Núm. Control", "Correo Institucional", "Clases", "Acciones"
        ])
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.horizontalHeader().setMinimumSectionSize(120)
        layout.addWidget(self.tabla, stretch=1)

        self.cargar_alumnos()
        self.mostrar_alumnos()

    def cargar_alumnos(self):
        self.alumnos = []
        if os.path.exists("alumnos.json"):
            with open("alumnos.json", "r", encoding="utf-8") as f:
                try:
                    self.alumnos = json.load(f)
                except json.JSONDecodeError:
                    self.alumnos = []

    def mostrar_alumnos(self, filtro=""):
        self.tabla.setRowCount(0)
        for idx, alumno in enumerate(self.alumnos):
            if filtro:
                texto = filtro.lower()
                if (texto not in alumno.get("nombre", "").lower() and
                    texto not in alumno.get("numero_control", "").lower()):
                    continue
            row = self.tabla.rowCount()
            self.tabla.insertRow(row)
            self.tabla.setItem(row, 0, QTableWidgetItem(alumno.get("nombre", "")))

            # Carrera editable con QComboBox
            combo_carrera = QComboBox()
            combo_carrera.addItems(CARRERAS)
            carrera_actual = alumno.get("carrera", "")
            if carrera_actual and carrera_actual not in CARRERAS:
                combo_carrera.addItem(carrera_actual)
            combo_carrera.setCurrentText(carrera_actual)
            combo_carrera.currentTextChanged.connect(lambda text, idx=idx: self.actualizar_carrera(idx, text))
            self.tabla.setCellWidget(row, 1, combo_carrera)

            self.tabla.setItem(row, 2, QTableWidgetItem(alumno.get("numero_control", "")))
            self.tabla.setItem(row, 3, QTableWidgetItem(alumno.get("correo", "")))
            clases = ", ".join(alumno.get("clases", [])) if "clases" in alumno else ""
            self.tabla.setItem(row, 4, QTableWidgetItem(clases))

            # Acciones: botón para ver clases y eliminar alumno
            acciones_widget = QWidget()
            acciones_layout = QHBoxLayout(acciones_widget)
            acciones_layout.setContentsMargins(0, 0, 0, 0)
            acciones_layout.setSpacing(4)

            btn_ver = QPushButton("Ver Clases")
            btn_ver.setStyleSheet("font-size: 14px; background-color: #A3BE8C; color: #23272f;")
            btn_ver.clicked.connect(lambda _, a=alumno: self.ver_clases_alumno(a))
            acciones_layout.addWidget(btn_ver)

            btn_eliminar = QPushButton("Eliminar")
            btn_eliminar.setStyleSheet("font-size: 14px; background-color: #BF616A; color: #ECEFF4;")
            btn_eliminar.clicked.connect(lambda _, idx=idx: self.eliminar_alumno(idx))
            acciones_layout.addWidget(btn_eliminar)

            self.tabla.setCellWidget(row, 5, acciones_widget)

    def buscar_alumnos(self):
        filtro = self.input_busqueda.text().strip()
        self.mostrar_alumnos(filtro)

    def actualizar_carrera(self, idx, nueva_carrera):
        if 0 <= idx < len(self.alumnos):
            self.alumnos[idx]["carrera"] = nueva_carrera

    def guardar_todos_los_cambios(self):
        with open("alumnos.json", "w", encoding="utf-8") as f:
            json.dump(self.alumnos, f, ensure_ascii=False, indent=2)
        QMessageBox.information(self, "Éxito", "Todos los cambios han sido guardados.")

    def ver_clases_alumno(self, alumno):
        clases = alumno.get("clases", [])
        if not clases:
            QMessageBox.information(self, "Clases", "El alumno no está inscrito en ninguna clase.")
            return
        msg = "\n".join(clases)
        QMessageBox.information(self, "Clases del Alumno", f"Clases inscritas:\n{msg}")

    def eliminar_alumno(self, idx):
        if 0 <= idx < len(self.alumnos):
            nombre = self.alumnos[idx].get("nombre", "")
            resp = QMessageBox.question(self, "Eliminar", f"¿Seguro que deseas eliminar a {nombre}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if resp == QMessageBox.StandardButton.Yes:
                del self.alumnos[idx]
                self.guardar_todos_los_cambios()
                self.mostrar_alumnos()