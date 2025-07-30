from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton,
    QFormLayout, QMessageBox, QHBoxLayout, QListWidget, QListWidgetItem # Añadido QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt
import json
import os

class RegistrarAlumnos(QWidget):
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
                font-size: 22px;
                border: 2px solid #00e1ff;
                border-radius: 10px;
                padding: 12px;
                margin-bottom: 18px;
            }
            QPushButton {
                background-color: #00e1ff;
                color: #1e2229;
                font-size: 22px;
                border-radius: 16px;
                font-weight: bold;
                padding: 18px 0;
                min-width: 220px;
            }
            QPushButton:hover {
                background-color: #00b3cc;
            }
            QListWidget { /* Estilos para el nuevo QListWidget */
                background: #2E3440; color: #ECEFF4; font-size: 18px;
                border: 2px solid #00e1ff; border-radius: 10px; padding: 10px;
            }
            QListWidget::item {
                padding: 8px; /* Ajusta el padding de los ítems si es necesario */
            }
            QListWidget::item:selected {
                background-color: #00e1ff; /* Color de fondo al seleccionar */
                color: #1e2229; /* Color de texto al seleccionar */
            }
        """)

        main_layout = QVBoxLayout(self) # Cambiado a main_layout para mayor claridad
        main_layout.setContentsMargins(60, 40, 60, 40)
        main_layout.setSpacing(24)

        lbl_titulo = QLabel("Registrar Alumno")
        lbl_titulo.setObjectName("titulo")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(lbl_titulo)

        form = QFormLayout()
        self.input_nombre = QLineEdit()
        self.input_carrera = QComboBox()
        self.input_carrera.addItems([
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
        self.input_numero_control = QLineEdit()
        self.input_numero_control.setPlaceholderText("Ejemplo: 21200903")
        self.input_correo = QLineEdit()
        self.input_correo.setReadOnly(True)

        # Vincular correo al número de control
        self.input_numero_control.textChanged.connect(self.actualizar_correo)

        form.addRow("Nombre completo:", self.input_nombre)
        form.addRow("Carrera:", self.input_carrera)
        form.addRow("Número de Control:", self.input_numero_control)
        form.addRow("Correo Institucional:", self.input_correo)

        main_layout.addLayout(form)

        # Sección para seleccionar clases (NUEVA SECCIÓN)
        clases_layout = QVBoxLayout()
        clases_label = QLabel("Clases a inscribir:")
        clases_label.setStyleSheet("font-size: 20px; color: #00e1ff; font-weight: bold;")
        clases_layout.addWidget(clases_label)

        self.lista_clases = QListWidget()
        self.lista_clases.setSelectionMode(QListWidget.SelectionMode.MultiSelection) # Permite seleccionar múltiples
        clases_layout.addWidget(self.lista_clases)
        self.cargar_clases_disponibles() # Llama a la nueva función para cargar clases

        main_layout.addLayout(clases_layout) # Añade el layout de clases al layout principal

        # Botón para registrar huella (simulado)
        btn_huella = QPushButton("Registrar Huella Dactilar")
        btn_huella.clicked.connect(self.registrar_huella)
        main_layout.addWidget(btn_huella)

        # Botón para registrar alumno
        btn_registrar = QPushButton("Registrar Alumno")
        btn_registrar.clicked.connect(self.registrar_alumno)
        main_layout.addWidget(btn_registrar)

        main_layout.addStretch()

        self.huella_asignada = None

    def actualizar_correo(self):
        nc = self.input_numero_control.text().strip()
        if nc:
            self.input_correo.setText(f"l{nc}@pachuca.tecnm.mx")
        else:
            self.input_correo.clear()

    def registrar_huella(self):
        # Aquí puedes poner tu lógica real de huella, por ahora solo simula
        self.huella_asignada = "huella_simulada"
        QMessageBox.information(self, "Huella", "Huella registrada correctamente (simulado).")

    def cargar_clases_disponibles(self):
        """Carga las clases disponibles de clases.json en la lista de selección."""
        self.lista_clases.clear()
        clases = []
        if os.path.exists("clases.json"):
            try:
                with open("clases.json", "r", encoding="utf-8") as f:
                    clases = json.load(f)
            except json.JSONDecodeError:
                QMessageBox.warning(self, "Error de Archivo", "El archivo clases.json está dañado o vacío. No se pudieron cargar las clases.")
                clases = [] # Asegura que clases sea una lista vacía en caso de error

        for clase in clases:
            # Asegúrate de que las claves existan antes de acceder
            materia = clase.get("materia", "Sin Materia")
            grupo = clase.get("grupo", "Sin Grupo")
            docente = clase.get("docente", "Sin Docente")
            # Crea un nombre único para la clase para mostrarlo y guardarlo
            nombre_clase_completo = f"{materia} - {grupo} ({docente})"
            item = QListWidgetItem(nombre_clase_completo)
            # Guarda los datos completos de la clase en el item, útil si necesitas más info al seleccionar
            item.setData(Qt.ItemDataRole.UserRole, clase)
            self.lista_clases.addItem(item)

    def registrar_alumno(self):
        nombre = self.input_nombre.text().strip()
        carrera = self.input_carrera.currentText()
        numero_control = self.input_numero_control.text().strip()
        correo = self.input_correo.text().strip()
        if not (nombre and carrera and numero_control and correo):
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios.")
            return
        if not self.huella_asignada:
            QMessageBox.warning(self, "Error", "Debes registrar la huella dactilar antes de guardar al alumno.")
            return

        # Obtener las clases seleccionadas
        clases_seleccionadas = []
        for item in self.lista_clases.selectedItems():
            clase_data = item.data(Qt.ItemDataRole.UserRole)
            # Construye el nombre de la clase tal como lo mostrarás y usarás para filtrar
            materia = clase_data.get("materia", "N/A")
            grupo = clase_data.get("grupo", "N/A")
            docente = clase_data.get("docente", "N/A")
            clases_seleccionadas.append(f"{materia} - {grupo} ({docente})")

        alumno = {
            'nombre': nombre,
            'carrera': carrera,
            'numero_control': numero_control,
            'correo': correo,
            'huella': self.huella_asignada,
            'clases': clases_seleccionadas # AÑADIDA ESTA LÍNEA para guardar las clases
        }

        # Guardar en alumnos.json
        alumnos = []
        if os.path.exists("alumnos.json"):
            with open("alumnos.json", "r", encoding="utf-8") as f:
                try:
                    alumnos = json.load(f)
                except json.JSONDecodeError:
                    alumnos = []

        # Para evitar duplicados si se edita un alumno existente, o añadir si es nuevo
        found = False
        for i, existing_alumno in enumerate(alumnos):
            if existing_alumno.get("numero_control") == numero_control:
                alumnos[i] = alumno # Actualiza el alumno existente
                found = True
                break
        if not found:
            alumnos.append(alumno) # Si no existe, lo añade

        with open("alumnos.json", "w", encoding="utf-8") as f:
            json.dump(alumnos, f, ensure_ascii=False, indent=2)

        QMessageBox.information(self, "Éxito", f"Alumno registrado correctamente.\nNúmero de Control: {numero_control}\nCorreo: {correo}")
        # Limpiar campos después de guardar
        self.input_nombre.clear()
        self.input_numero_control.clear()
        self.input_correo.clear()
        self.lbl_huella.clear() # Limpia la huella visual si existe (asumiendo que lbl_huella existe)
        self.huella_asignada = None # Resetea el estado de la huella
        self.lista_clases.clearSelection() # Deselecciona las clases