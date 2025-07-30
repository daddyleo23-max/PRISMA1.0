from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QMessageBox, QListWidget, QComboBox, QFormLayout, QListWidgetItem
)
from PyQt6.QtCore import Qt, QTimer # Importar QTimer
from PyQt6.QtGui import QPixmap
import json
import os

# --- Definición de la ruta base del proyecto ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(BASE_DIR, '..')

# Función auxiliar para obtener la ruta completa de un archivo JSON o imagen
def get_json_path(filename):
    return os.path.join(PROJECT_ROOT, filename)

class RegistroMasivoHuellas(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registro Masivo de Alumnos y Huellas")
        self.setMinimumSize(1200, 700) # Manteniendo el tamaño original del archivo que me pasaste
        self.setStyleSheet("""
            QDialog { /* Aplicar estilo a QDialog directamente */
                background-color: #23272f;
                border-radius: 18px;
            }
            QLabel#titulo { color: #00e1ff; font-size: 32px; font-weight: bold; margin-bottom: 18px; }
            QLabel { color: #A3BE8C; font-size: 20px; font-weight: bold; }
            QLineEdit, QComboBox {
                background: #2E3440; color: #00e1ff; font-size: 22px;
                border: 2px solid #00e1ff; border-radius: 10px; padding: 12px; margin-bottom: 18px;
            }
            QPushButton {
                background-color: #00e1ff; color: #1e2229; font-size: 22px;
                border-radius: 16px; font-weight: bold; padding: 14px 0; min-width: 220px;
            }
            QPushButton:hover { background-color: #00b3cc; }
            QListWidget { /* Estilo para el QListWidget de clases y el de registrados */
                background: #2E3440; color: #00e1ff; font-size: 18px;
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

        self.registros_sesion = []
        self.alumnos_json = self.cargar_alumnos()
        self.clases_json = self.cargar_clases()
        self.alumno_actual = None
        self.huella_asignada_simulada = None # Variable para almacenar la huella simulada

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(18)

        lbl_titulo = QLabel("Registro Masivo de Alumnos y Huellas")
        lbl_titulo.setObjectName("titulo")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(lbl_titulo)

        h_layout = QHBoxLayout()
        h_layout.setSpacing(40)
        main_layout.addLayout(h_layout)

        # --- Parte izquierda: datos del alumno y registro de huella ---
        left_layout = QVBoxLayout()
        left_layout.setSpacing(18)
        h_layout.addLayout(left_layout, stretch=2)

        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(15)

        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre completo del alumno")
        form_layout.addRow("Nombre:", self.input_nombre)

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
        form_layout.addRow("Carrera:", self.input_carrera)

        self.input_nc = QLineEdit()
        self.input_nc.setPlaceholderText("Número de control")
        self.input_nc.returnPressed.connect(self.buscar_alumno)
        self.input_nc.textChanged.connect(self.actualizar_correo)
        form_layout.addRow("Número de Control:", self.input_nc)

        self.input_correo = QLineEdit()
        self.input_correo.setPlaceholderText("Correo electrónico")
        self.input_correo.setReadOnly(True)
        form_layout.addRow("Correo:", self.input_correo)
        
        left_layout.addLayout(form_layout)

        clases_layout = QVBoxLayout()
        clases_label = QLabel("Clases a inscribir (selección múltiple):")
        clases_label.setStyleSheet("font-size: 20px; color: #00e1ff; font-weight: bold; margin-top: 15px;")
        clases_layout.addWidget(clases_label)

        self.lista_clases = QListWidget()
        self.lista_clases.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        clases_layout.addWidget(self.lista_clases)
        self.cargar_clases_disponibles()
        left_layout.addLayout(clases_layout)

        # Área de huella
        self.lbl_huella_instruccion = QLabel("Coloca la huella del alumno aquí:")
        left_layout.addWidget(self.lbl_huella_instruccion)
        self.lbl_huella = QLabel()
        self.lbl_huella.setFixedSize(150, 150) # Aumentar tamaño del área de huella
        self.lbl_huella.setStyleSheet("background: #2E3440; border-radius: 75px; border: 2px solid #00e1ff;")
        self.lbl_huella.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.lbl_huella, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn_registrar_huella = QPushButton("Registrar Huella y Datos")
        self.btn_registrar_huella.clicked.connect(self.registrar_huella_simulada) # Conectar al método de simulación
        self.btn_registrar_huella.setEnabled(False)
        left_layout.addWidget(self.btn_registrar_huella)

        left_layout.addStretch()

        # --- Parte derecha: lista de registrados en la sesión ---
        right_layout = QVBoxLayout()
        right_layout.setSpacing(18)
        h_layout.addLayout(right_layout, stretch=1)

        lbl_lista = QLabel("Alumnos registrados en esta sesión:")
        lbl_lista.setStyleSheet("color: #00e1ff; font-size: 20px; font-weight: bold;")
        right_layout.addWidget(lbl_lista)

        self.lista_registrados = QListWidget()
        right_layout.addWidget(self.lista_registrados)

        self.btn_guardar_todo = QPushButton("Guardar Todos los Cambios")
        self.btn_guardar_todo.clicked.connect(self.guardar_todos)
        right_layout.addWidget(self.btn_guardar_todo)

        right_layout.addStretch()
        
        self.limpiar_campos_alumno()

    def cargar_alumnos(self):
        """Carga los datos de alumnos desde alumnos.json."""
        alumnos_path = get_json_path("alumnos.json")
        if os.path.exists(alumnos_path):
            with open(alumnos_path, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def cargar_clases(self):
        """Carga los datos de clases desde clases.json."""
        clases_path = get_json_path("clases.json")
        if os.path.exists(clases_path):
            with open(clases_path, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def cargar_clases_disponibles(self):
        """Carga las clases disponibles de clases.json en la lista de selección."""
        self.lista_clases.clear()
        clases = []
        clases_path = get_json_path("clases.json")
        if os.path.exists(clases_path):
            try:
                with open(clases_path, "r", encoding="utf-8") as f:
                    clases = json.load(f)
            except json.JSONDecodeError:
                QMessageBox.warning(self, "Error de Archivo", "El archivo clases.json está dañado o vacío. No se pudieron cargar las clases.")
                clases = []

        for clase in clases:
            materia = clase.get("materia", "Sin Materia")
            grupo = clase.get("grupo", "Sin Grupo")
            docente = clase.get("docente", "Sin Docente")
            nombre_clase_completo = f"{materia} - {grupo} ({docente})"
            item = QListWidgetItem(nombre_clase_completo)
            item.setData(Qt.ItemDataRole.UserRole, clase)
            self.lista_clases.addItem(item)

    def actualizar_correo(self):
        """Actualiza el campo de correo institucional basado en el número de control."""
        nc = self.input_nc.text().strip()
        if nc:
            self.input_correo.setText(f"l{nc}@pachuca.tecnm.mx")
        else:
            self.input_correo.clear()

    def buscar_alumno(self):
        """
        Busca un alumno por número de control y precarga sus datos.
        Si no lo encuentra, permite ingresar nuevos datos.
        """
        nc = self.input_nc.text().strip()
        if not nc:
            QMessageBox.warning(self, "Advertencia", "Por favor, ingresa un número de control para buscar.")
            self.limpiar_campos_alumno()
            return

        alumno_encontrado = next((a for a in self.alumnos_json if a.get("numero_control") == nc), None)
        
        if alumno_encontrado:
            self.alumno_actual = alumno_encontrado
            self.input_nombre.setText(self.alumno_actual.get('nombre', ''))
            carrera_index = self.input_carrera.findText(self.alumno_actual.get('carrera', ''))
            if carrera_index >= 0:
                self.input_carrera.setCurrentIndex(carrera_index)
            else:
                self.input_carrera.setCurrentIndex(0)

            self.input_correo.setText(self.alumno_actual.get('correo', ''))
            self.btn_registrar_huella.setEnabled(True)
            self.lbl_huella.clear()
            if "clases" in self.alumno_actual and isinstance(self.alumno_actual["clases"], list):
                for i in range(self.lista_clases.count()):
                    item = self.lista_clases.item(i)
                    if item.text() in self.alumno_actual["clases"]:
                        item.setSelected(True)
                    else:
                        item.setSelected(False)
            else:
                self.lista_clases.clearSelection()

            QMessageBox.information(self, "Alumno Encontrado", f"Datos de {self.alumno_actual.get('nombre')} cargados. Puedes registrar su huella o actualizar datos.")
        else:
            self.alumno_actual = {"numero_control": nc, "huella": None, "clases": []}
            self.limpiar_campos_alumno(keep_nc=True)
            self.btn_registrar_huella.setEnabled(True)
            self.lbl_huella.clear()
            QMessageBox.information(self, "Alumno Nuevo", "Número de control no encontrado. Ingresa los datos del nuevo alumno y registra su huella.")

    def registrar_huella_simulada(self):
        """
        Inicia la simulación del registro de huella y datos.
        """
        if not self.alumno_actual:
            QMessageBox.warning(self, "Error", "Primero busca un alumno o ingresa un nuevo número de control.")
            return

        nombre = self.input_nombre.text().strip()
        carrera = self.input_carrera.currentText()
        correo = self.input_correo.text().strip()
        nc = self.input_nc.text().strip()

        if not (nombre and carrera and nc and correo):
            QMessageBox.warning(self, "Error de Datos", "Todos los campos (Nombre, Carrera, Número de Control, Correo) son obligatorios.")
            return

        self.btn_registrar_huella.setEnabled(False) # Deshabilitar el botón durante la simulación
        self.lbl_huella.clear()
        self.lbl_huella.setText("Registrando huella...") # Mensaje temporal
        
        # Simular un retraso de 1 segundo para el registro de huella
        QTimer.singleShot(1000, self._completar_registro_huella)

    def _completar_registro_huella(self):
        """
        Completa el registro de huella y datos después de la simulación.
        """
        nombre = self.input_nombre.text().strip()
        carrera = self.input_carrera.currentText()
        correo = self.input_correo.text().strip()
        nc = self.input_nc.text().strip()

        # Simular registro de huella
        pixmap = QPixmap(get_json_path("Images/huella.png")) 
        if pixmap.isNull():
            self.lbl_huella.setText("Huella registrada")
            self.huella_asignada_simulada = "huella_simulada_generica" # Fallback si no hay imagen
            QMessageBox.warning(self, "Advertencia de Imagen", "No se encontró la imagen 'huella.png'. Se usará un texto de marcador de posición.")
        else:
            self.lbl_huella.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)) # Usar el tamaño más grande
            self.huella_asignada_simulada = "huella_simulada_con_imagen"

        # Actualizar datos del alumno_actual
        self.alumno_actual['nombre'] = nombre
        self.alumno_actual['carrera'] = carrera
        self.alumno_actual['correo'] = correo
        self.alumno_actual['huella'] = self.huella_asignada_simulada # Asignar la huella simulada

        # Obtener las clases seleccionadas del QListWidget
        clases_seleccionadas = []
        for item in self.lista_clases.selectedItems():
            clases_seleccionadas.append(item.text())
        
        self.alumno_actual["clases"] = clases_seleccionadas

        # Añadir a registros_sesion si es nuevo en esta sesión o actualizar si ya está
        if not any(a.get("numero_control") == self.alumno_actual.get("numero_control") for a in self.registros_sesion):
            self.registros_sesion.append(self.alumno_actual.copy())
            self.lista_registrados.addItem(f"{self.alumno_actual['nombre']} ({self.alumno_actual['numero_control']})")
        else:
            for i, reg in enumerate(self.registros_sesion):
                if reg.get("numero_control") == self.alumno_actual.get("numero_control"):
                    self.registros_sesion[i] = self.alumno_actual.copy()
                    self.lista_registrados.item(i).setText(f"{self.alumno_actual['nombre']} ({self.alumno_actual['numero_control']})")
                    break

        QMessageBox.information(self, "Registro Exitoso", f"Huella y datos de {nombre} registrados/actualizados correctamente.")
        self.limpiar_campos_alumno()
        self.btn_registrar_huella.setEnabled(False) # Deshabilitar después de limpiar
        self.alumno_actual = None

    def guardar_todos(self):
        """
        Guarda todos los cambios de la sesión en alumnos.json.
        """
        for reg_sesion in self.registros_sesion:
            found = False
            for i, alumno_existente in enumerate(self.alumnos_json):
                if alumno_existente.get("numero_control") == reg_sesion.get("numero_control"):
                    self.alumnos_json[i] = reg_sesion
                    found = True
                    break
            if not found:
                self.alumnos_json.append(reg_sesion)

        alumnos_path = get_json_path("alumnos.json")
        try:
            with open(alumnos_path, "w", encoding="utf-8") as f:
                json.dump(self.alumnos_json, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "Guardado", "Todos los cambios han sido guardados en alumnos.json.")
            self.registros_sesion.clear()
            self.lista_registrados.clear()
            self.alumnos_json = self.cargar_alumnos()
        except Exception as e:
            QMessageBox.critical(self, "Error de Guardado", f"No se pudieron guardar los cambios: {e}")

    def limpiar_campos_alumno(self, keep_nc=False):
        """
        Limpia los campos de entrada de datos del alumno.
        Si keep_nc es True, mantiene el número de control.
        """
        if not keep_nc:
            self.input_nc.clear()
        self.input_nombre.clear()
        self.input_carrera.setCurrentIndex(0)
        self.input_correo.clear()
        self.lbl_huella.clear()
        self.lbl_huella.setText("Huella no registrada")
        self.btn_registrar_huella.setEnabled(False) # Asegurarse de que esté deshabilitado al limpiar
        self.alumno_actual = None
        self.lista_clases.clearSelection()

