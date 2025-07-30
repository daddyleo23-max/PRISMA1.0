import sys
import json
import datetime
import os
from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QDialog, QVBoxLayout, QWidget,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QApplication, QSizePolicy, QGraphicsBlurEffect, QLineEdit, QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QTime, QPoint, QSize
from PyQt6.QtGui import QPainter, QPolygon, QColor, QPen

# --- Definición de la ruta base del proyecto ---
# Esto asume que CentralBienvenida.py está en D_S_P/ControlEntrada/
# y los JSON están en D_S_P/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(BASE_DIR, '..')

# Función auxiliar para obtener la ruta completa de un archivo JSON
def get_json_path(filename):
    return os.path.join(PROJECT_ROOT, filename)

class PanelAsistenciasDocentes(QFrame):
    """
    Panel que muestra la tabla de asistencias de docentes.
    """
    def __init__(self, docentes, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        # Ajustar márgenes y espaciado del layout interno para maximizar espacio de tabla
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30) # Reducir márgenes para más espacio
        layout.setSpacing(15) # Reducir espaciado entre elementos

        titulo = QLabel("Asistencias de Docentes")
        # Ajustar margen inferior para que el texto esté más arriba
        titulo.setStyleSheet("font-size: 36px; color: #00e1ff; font-weight: bold; margin-bottom: 10px;")
        # Alinear el título arriba y al centro
        layout.addWidget(titulo, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        self.tabla = QTableWidget(len(docentes), 4)
        self.tabla.setHorizontalHeaderLabels(["Docente", "Estado", "Hora de llegada", "Hora de salida"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.tabla.setStyleSheet("""
            QTableWidget {
                background-color: #23272f;
                color: #fff;
                font-size: 22px; /* Mantener tamaño de fuente para legibilidad */
                border: 2px solid #00e1ff;
                border-radius: 18px; /* Bordes redondeados */
                padding: 8px; /* Padding general */
            }
            QHeaderView::section {
                background-color: #00e1ff;
                color: #1e2229; /* Color de texto más oscuro para contraste */
                font-size: 22px; /* Consistente con el cuerpo */
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #1e2229; /* Borde inferior para separar encabezado */
                border-radius: 0px;
                padding: 18px; /* Padding en encabezados */
            }
            QTableWidget::item {
                border-bottom: 1px solid #4C566A; /* Borde más sutil entre filas */
                padding: 16px; /* Padding en celdas */
            }
            QTableWidget::item:last-child {
                border-bottom: none; /* Eliminar borde inferior de la última fila */
            }
        """)
        # Aumentar el tamaño mínimo y máximo para que ocupe casi todo el volumen
        self.tabla.setMinimumWidth(900)
        self.tabla.setMaximumWidth(1400)
        self.tabla.setMinimumHeight(600) # Aumentado significativamente
        self.tabla.setMaximumHeight(900) # Aumentado significativamente
        for i, docente in enumerate(docentes):
            item_nombre = QTableWidgetItem(docente["nombre"])
            item_nombre.setForeground(QColor("#00e1ff"))
            item_nombre.setFont(self.tabla.font())
            self.tabla.setItem(i, 0, item_nombre)

            item_estado = QTableWidgetItem("Ausente")
            item_estado.setForeground(QColor("#ff4d4d"))
            item_estado.setFont(self.tabla.font())
            self.tabla.setItem(i, 1, item_estado)

            self.tabla.setItem(i, 2, QTableWidgetItem(""))
            self.tabla.setItem(i, 3, QTableWidgetItem(""))

        layout.addWidget(self.tabla, alignment=Qt.AlignmentFlag.AlignCenter) # Centrar la tabla

    def marcar_asistencia(self, nombre_docente):
        hora = QTime.currentTime().toString("HH:mm:ss")
        for i in range(self.tabla.rowCount()):
            if self.tabla.item(i, 0).text() == nombre_docente:
                item_estado = QTableWidgetItem("Presente")
                item_estado.setForeground(QColor("#00ffb3"))
                item_estado.setFont(self.tabla.font())
                self.tabla.setItem(i, 1, item_estado)
                if not self.tabla.item(i, 2).text():
                    self.tabla.setItem(i, 2, QTableWidgetItem(hora))
                break

    def marcar_salida(self, nombre_docente):
        hora = QTime.currentTime().toString("HH:mm:ss")
        for i in range(self.tabla.rowCount()):
            if self.tabla.item(i, 0).text() == nombre_docente:
                self.tabla.setItem(i, 3, QTableWidgetItem(hora))
                item_estado = QTableWidgetItem("Salió")
                item_estado.setForeground(QColor("#ffb347"))
                item_estado.setFont(self.tabla.font())
                self.tabla.setItem(i, 1, item_estado)
                break

class RelojAnalogico(QWidget):
    """
    Widget para mostrar un reloj analógico.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(160, 160) # Increased clock size
        timer = QTimer(self)
        timer.timeout.connect(self.update)
        timer.start(1000)

    def paintEvent(self, event):
        side = min(self.width(), self.height())
        time = QTime.currentTime()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(side / 200.0, side / 200.0)

        # Manecilla de hora
        hour_hand = QPolygon([QPoint(7, 8), QPoint(-7, 8), QPoint(0, -50)])
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#00e1ff"))
        painter.save()
        painter.rotate(30.0 * ((time.hour() + time.minute() / 60.0)))
        painter.drawConvexPolygon(hour_hand)
        painter.restore()

        # Manecilla de minutos
        minute_hand = QPolygon([QPoint(7, 8), QPoint(-7, 8), QPoint(0, -70)])
        painter.setBrush(QColor("#ffffff"))
        painter.save()
        painter.rotate(6.0 * (time.minute() + time.second() / 60.0))
        painter.drawConvexPolygon(minute_hand)
        painter.restore()

        # Manecilla de segundos
        second_hand = QPolygon([QPoint(2, 8), QPoint(-2, 8), QPoint(0, -80)])
        painter.setBrush(QColor("#ff4d4d"))
        painter.save()
        painter.rotate(6.0 * time.second())
        painter.drawConvexPolygon(second_hand)
        painter.restore()

        # Dibujar marcas del reloj
        painter.setPen(QPen(QColor("#00e1ff"), 2))
        for i in range(12):
            painter.drawLine(0, -88, 0, -96)
            painter.rotate(30.0)
        painter.setPen(QPen(QColor("#ffffff"), 1))
        for i in range(60):
            if i % 5 != 0:
                painter.drawLine(0, -92, 0, -96)
            painter.rotate(6.0)

class VerSalonesActivosDialog(QDialog):
    """
    Diálogo para ver salones con clases activas y la asistencia de alumnos.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Salones Activos y Asistencia")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet("""
            QDialog {
                background-color: #23272f;
                border-radius: 18px;
            }
            QLabel#titulo_dialog {
                color: #00e1ff;
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 18px;
            }
            QPushButton.salon_button {
                background-color: #3B4252;
                color: #ECEFF4;
                font-size: 20px;
                border-radius: 12px;
                padding: 15px;
                text-align: left;
                margin-bottom: 10px;
            }
            QPushButton.salon_button:hover {
                background-color: #4C566A;
            }
            QPushButton.salon_button:checked {
                background-color: #5E81AC;
                border: 2px solid #00e1ff;
            }
            QTableWidget {
                background-color: #3B4252;
                border: 1px solid #4C566A;
                border-radius: 8px;
                font-size: 16px;
                color: #ECEFF4;
            }
            QHeaderView::section {
                background-color: #4C566A;
                color: #00e1ff;
                font-size: 16px;
                font-weight: bold;
                padding: 8px;
                border: none;
            }
            QLineEdit {
                background: #2E3440;
                color: #00e1ff;
                font-size: 18px;
                border: 2px solid #00e1ff;
                border-radius: 10px;
                padding: 10px;
                margin-bottom: 10px;
            }
            QLabel {
                color: #A3BE8C;
                font-size: 16px;
            }
        """)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(25)

        # Columna Izquierda: Lista de Salones Activos
        self.left_panel = QVBoxLayout()
        self.lbl_salones_activos = QLabel("Salones con Clase Activa:")
        self.lbl_salones_activos.setObjectName("titulo_dialog")
        self.left_panel.addWidget(self.lbl_salones_activos)

        self.scroll_area_salones = QScrollArea()
        self.scroll_area_salones.setWidgetResizable(True)
        self.scroll_area_salones.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.salones_container = QWidget()
        self.salones_layout = QVBoxLayout(self.salones_container)
        self.salones_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.salones_layout.setSpacing(10)
        self.scroll_area_salones.setWidget(self.salones_container)
        self.left_panel.addWidget(self.scroll_area_salones)
        self.main_layout.addLayout(self.left_panel, 1)

        # Columna Derecha: Detalles de Clase y Asistencia
        self.right_panel = QVBoxLayout()
        self.lbl_clase_info = QLabel("Selecciona un salón para ver los detalles de la clase.")
        self.lbl_clase_info.setStyleSheet("color: #00e1ff; font-size: 22px; font-weight: bold; margin-bottom: 15px;")
        self.lbl_clase_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.right_panel.addWidget(self.lbl_clase_info)

        self.input_busqueda_alumno = QLineEdit()
        self.input_busqueda_alumno.setPlaceholderText("Buscar alumno por nombre o número de control...")
        self.input_busqueda_alumno.textChanged.connect(self.filtrar_alumnos)
        self.right_panel.addWidget(self.input_busqueda_alumno)

        self.tabla_asistencia = QTableWidget()
        self.tabla_asistencia.setColumnCount(5)
        self.tabla_asistencia.setHorizontalHeaderLabels(["#", "Nombre", "Núm. Control", "Hora Llegada", "Estado"])
        self.tabla_asistencia.verticalHeader().setVisible(False)
        self.tabla_asistencia.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_asistencia.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.right_panel.addWidget(self.tabla_asistencia)
        self.main_layout.addLayout(self.right_panel, 2)

        self.salones_activos_data = {} # Almacena datos de salones activos
        self.current_selected_salon = None # Almacena el salón actualmente seleccionado
        self.alumnos_clase_actual = [] # Alumnos de la clase seleccionada

        self.cargar_salones_activos()
        self.timer_actualizacion = QTimer(self)
        self.timer_actualizacion.timeout.connect(self.cargar_salones_activos)
        self.timer_actualizacion.start(5000) # Actualizar cada 5 segundos

    def cargar_salones_activos(self):
        """
        Lee estado_clase_actual.json y asistencia_clase_actual.json
        para mostrar los salones con clases activas.
        """
        print("VerSalonesActivosDialog: Cargando salones activos...")
        self.salones_activos_data = {} # Resetear datos
        
        estado_clase_path = get_json_path("estado_clase_actual.json")
        asistencia_clase_path = get_json_path("asistencia_clase_actual.json")

        try:
            if os.path.exists(estado_clase_path):
                with open(estado_clase_path, "r", encoding="utf-8") as f:
                    estado_clase = json.load(f)
                
                if estado_clase.get("activa"):
                    salon_nombre = estado_clase.get("salon")
                    if salon_nombre:
                        self.salones_activos_data[salon_nombre] = {
                            "clase_info": estado_clase,
                            "alumnos": []
                        }
                        # Cargar asistencia de este salón
                        if os.path.exists(asistencia_clase_path):
                            with open(asistencia_clase_path, "r", encoding="utf-8") as f_asistencia:
                                self.salones_activos_data[salon_nombre]["alumnos"] = json.load(f_asistencia)
            else:
                print("VerSalonesActivosDialog: estado_clase_actual.json no encontrado.")
        except json.JSONDecodeError as e:
            print(f"VerSalonesActivosDialog: Error al leer JSON de estado/asistencia: {e}")
        except Exception as e:
            print(f"VerSalonesActivosDialog: Error inesperado al cargar salones activos: {e}")

        self.actualizar_lista_salones_ui()

    def actualizar_lista_salones_ui(self):
        """
        Actualiza los botones de salones activos en la interfaz.
        """
        # Limpiar botones existentes
        for i in reversed(range(self.salones_layout.count())):
            widget = self.salones_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if not self.salones_activos_data:
            lbl_no_salones = QLabel("No hay salones con clases activas en este momento.")
            lbl_no_salones.setStyleSheet("color: #ff4d4d; font-size: 18px; alignment: center; padding: 20px;")
            self.salones_layout.addWidget(lbl_no_salones)
            self.lbl_clase_info.setText("Selecciona un salón para ver los detalles de la clase.")
            self.tabla_asistencia.setRowCount(0)
            self.alumnos_clase_actual = []
            self.current_selected_salon = None
            return

        for salon_nombre, data in self.salones_activos_data.items():
            clase_info = data["clase_info"]
            btn = QPushButton(
                f"Salón: {salon_nombre}\n"
                f"Clase: {clase_info.get('materia', 'N/A')} - {clase_info.get('grupo', 'N/A')}\n"
                f"Docente: {clase_info.get('docente', 'N/A')}\n"
                f"Inicio: {clase_info.get('hora_inicio_real', 'N/A')}"
            )
            btn.setObjectName("salon_button")
            btn.setCheckable(True) # Para que se vea seleccionado
            btn.clicked.connect(lambda _, s=salon_nombre: self.seleccionar_salon(s))
            self.salones_layout.addWidget(btn)

            # Si el salón actualmente seleccionado sigue activo, re-seleccionarlo
            if self.current_selected_salon == salon_nombre:
                btn.setChecked(True)
                self.seleccionar_salon(salon_nombre) # Volver a cargar los detalles

    def seleccionar_salon(self, salon_nombre):
        """
        Muestra los detalles de la clase y la asistencia para el salón seleccionado.
        """
        print(f"VerSalonesActivosDialog: Salón seleccionado: {salon_nombre}")
        self.current_selected_salon = salon_nombre

        # Desmarcar otros botones
        for i in range(self.salones_layout.count()):
            widget = self.salones_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton) and widget.objectName() == "salon_button":
                if widget.text().startswith(f"Salón: {salon_nombre}"):
                    widget.setChecked(True)
                else:
                    widget.setChecked(False)

        data = self.salones_activos_data.get(salon_nombre)
        if data:
            clase_info = data["clase_info"]
            self.alumnos_clase_actual = data["alumnos"] # Cargar alumnos para este salón
            
            self.lbl_clase_info.setText(
                f"<b>Detalles de la Clase en {salon_nombre}:</b><br>"
                f"Materia: {clase_info.get('materia', 'N/A')} - Grupo: {clase_info.get('grupo', 'N/A')}<br>"
                f"Docente: {clase_info.get('docente', 'N/A')}<br>"
                f"Hora de Inicio: {clase_info.get('hora_inicio_real', 'N/A')}"
            )
            self.lbl_clase_info.setTextFormat(Qt.TextFormat.RichText)
            self.actualizar_tabla_asistencia_dialog()
            self.input_busqueda_alumno.clear() # Limpiar búsqueda al cambiar de salón
        else:
            self.lbl_clase_info.setText("Error: Información del salón no encontrada.")
            self.tabla_asistencia.setRowCount(0)
            self.alumnos_clase_actual = []

    def actualizar_tabla_asistencia_dialog(self, alumnos_a_mostrar=None):
        """
        Actualiza la tabla de asistencia en el diálogo.
        Permite filtrar la lista de alumnos.
        """
        if alumnos_a_mostrar is None:
            alumnos_a_mostrar = self.alumnos_clase_actual

        self.tabla_asistencia.setRowCount(len(alumnos_a_mostrar))
        for idx, alumno in enumerate(alumnos_a_mostrar):
            self.tabla_asistencia.setItem(idx, 0, QTableWidgetItem(str(idx + 1)))
            self.tabla_asistencia.setItem(idx, 1, QTableWidgetItem(alumno.get('nombre', '')))
            self.tabla_asistencia.setItem(idx, 2, QTableWidgetItem(alumno.get('numero_control', '')))
            self.tabla_asistencia.setItem(idx, 3, QTableWidgetItem(alumno.get('hora_llegada', '--:--:--')))
            
            estado_item = QTableWidgetItem(alumno.get('estado', 'Desconocido'))
            if alumno.get('estado') == "🟢 A tiempo":
                estado_item.setForeground(QColor("#A3BE8C")) # Green
            elif alumno.get('estado') == "🟡 Retardo moderado":
                estado_item.setForeground(QColor("#EBCB8B")) # Yellow
            elif alumno.get('estado') == "🔴 Retardo grave":
                estado_item.setForeground(QColor("#BF616A")) # Red
            else: # Not registered
                estado_item.setForeground(QColor("#81A1C1")) # Light blue
            self.tabla_asistencia.setItem(idx, 4, estado_item)

    def filtrar_alumnos(self, texto):
        """
        Filters the student list in the attendance table based on the search text.
        """
        filtro = texto.lower()
        alumnos_filtrados = []
        for alumno in self.alumnos_clase_actual:
            nombre = alumno.get('nombre', '').lower()
            numero_control = alumno.get('numero_control', '').lower()
            if filtro in nombre or filtro in numero_control:
                alumnos_filtrados.append(alumno)
        self.actualizar_tabla_asistencia_dialog(alumnos_filtrados)

class CentralBienvenida(QMainWindow):
    """
    Main welcome window, displays clock, teacher attendance
    and action buttons, including "View Classrooms".
    """
    def __init__(self, docentes):
        super().__init__()
        self.setWindowTitle("Bienvenida - DSP")
        self.setStyleSheet("background-color: #1e2229;")
        self.docentes = docentes

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout_principal = QHBoxLayout(central_widget)
        self.layout_principal.setContentsMargins(60, 60, 60, 60) # Increased general margins
        self.layout_principal.setSpacing(60) # Increased spacing between panels

        # Left panel: stacked buttons and clock
        panel_izquierdo = QVBoxLayout()
        panel_izquierdo.setSpacing(40) # Increased vertical spacing in the left panel

        self.label = QLabel("¡Bienvenido al Departamento de Sistemas!", self)
        self.label.setStyleSheet("color: white; font-size: 36px; font-weight: bold; margin-bottom: 20px;") # Increased font size and margin
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_izquierdo.addWidget(self.label)

        # Container for clocks
        relojes_container = QVBoxLayout()
        relojes_container.setSpacing(20) # Spacing between clocks
        relojes_container.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Large and centered digital clock
        self.lbl_reloj = QLabel(self)
        self.lbl_reloj.setStyleSheet("color: #00e1ff; font-size: 48px; font-weight: bold;") # Larger
        self.lbl_reloj.setAlignment(Qt.AlignmentFlag.AlignCenter)
        relojes_container.addWidget(self.lbl_reloj)

        # Large and centered analog clock
        self.reloj_analogico = RelojAnalogico(self)
        reloj_analogico_layout = QHBoxLayout() # To center the analog clock
        reloj_analogico_layout.addStretch()
        reloj_analogico_layout.addWidget(self.reloj_analogico)
        reloj_analogico_layout.addStretch()
        relojes_container.addLayout(reloj_analogico_layout)

        panel_izquierdo.addLayout(relojes_container)

        # Stacked buttons vertically, appropriate size
        botones_layout = QVBoxLayout()
        botones_layout.setSpacing(25) # Spacing between buttons

        btn_style = """
            QPushButton {
                background-color: #00e1ff;
                color: #1e2229;
                font-size: 24px; /* Larger */
                border-radius: 16px; /* More rounded */
                font-weight: bold;
                padding: 20px 0; /* More vertical padding */
                min-width: 240px; /* Minimum width */
                min-height: 60px; /* Minimum height */
                max-width: 300px; /* Maximum width */
                box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.3); /* Shadow for depth */
            }
            QPushButton:hover {
                background-color: #00b3cc;
                box-shadow: 0px 10px 20px rgba(0, 0, 0, 0.4); /* Larger shadow on hover */
            }
        """

        self.btn_abrir = QPushButton("Abrir\nDepartamento", self)
        self.btn_abrir.setStyleSheet(btn_style)
        self.btn_abrir.clicked.connect(self.solicitar_huella_abrir)
        botones_layout.addWidget(self.btn_abrir, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn_cerrar = QPushButton("Cerrar\nDepartamento", self)
        self.btn_cerrar.setStyleSheet(btn_style.replace("#00e1ff", "#ff4d4d").replace("#00b3cc", "#cc0000"))
        self.btn_cerrar.clicked.connect(self.solicitar_huella_cerrar)
        botones_layout.addWidget(self.btn_cerrar, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn_salones = QPushButton("Ver\nSalones", self)
        self.btn_salones.setStyleSheet(btn_style.replace("#00e1ff", "#00ffb3").replace("#00b3cc", "#00cc8a"))
        self.btn_salones.clicked.connect(self.solicitar_huella_salones)
        botones_layout.addWidget(self.btn_salones, alignment=Qt.AlignmentFlag.AlignCenter)

        panel_izquierdo.addLayout(botones_layout)
        panel_izquierdo.addStretch() # Pushes elements upwards
        self.layout_principal.addLayout(panel_izquierdo, 1)

        # Right panel: teacher attendance (controlled width)
        self.panel_asistencias = PanelAsistenciasDocentes(docentes, self)
        self.panel_asistencias.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout_principal.addWidget(self.panel_asistencias, 2)

        self.actualizar_reloj_digital() # Initial call for the digital clock

    def solicitar_huella_abrir(self):
        self.solicitar_huella(action_callback=self.abrir_departamento)

    def solicitar_huella_salones(self):
        self.solicitar_huella(action_callback=self.mostrar_dialogo_salones_activos)

    def solicitar_huella_cerrar(self):
        self.solicitar_huella(action_callback=self.cerrar_departamento)

    def solicitar_huella(self, action_callback=None):
        """
        Displays a fingerprint verification dialog and executes a callback if successful.
        """
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(10)
        self.setGraphicsEffect(blur)
        dialog = QDialog(self)
        dialog.setWindowTitle("Verificación de Huella")
        dialog.setModal(True)
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowType.FramelessWindowHint)
        dialog.setStyleSheet("""
            background-color: #23272f;
            border-radius: 20px;
        """)
        layout = QVBoxLayout(dialog)
        label = QLabel("Por favor, coloque su huella\nen el sensor...", dialog)
        label.setStyleSheet("color: white; font-size: 20px; font-weight: bold; padding: 20px;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        dialog.setFixedSize(420, 160)
        
        # Simulate correct fingerprint after 2 seconds
        QTimer.singleShot(2000, dialog.accept)
        
        result = dialog.exec()
        self.setGraphicsEffect(None)

        if result == QDialog.DialogCode.Accepted and action_callback:
            action_callback()
        elif result != QDialog.DialogCode.Accepted:
            QMessageBox.warning(self, "Acceso Denegado", "Verificación de huella fallida o cancelada.")

    def abrir_departamento(self):
        """
        Simulates the action of opening the department.
        """
        QMessageBox.information(self, "Departamento Abierto", "¡Departamento abierto correctamente!")
        # Here you could add logic to change the department's status in a JSON, etc.

    def cerrar_departamento(self):
        """
        Simulates the action of closing the department and closes the application.
        """
        self.mostrar_despedida()

    def mostrar_despedida(self):
        """
        Displays a farewell message before closing the application.
        """
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(10)
        self.setGraphicsEffect(blur)
        dialog = QDialog(self)
        dialog.setWindowTitle("Hasta luego")
        dialog.setModal(True)
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowType.FramelessWindowHint)
        dialog.setStyleSheet("""
            background-color: #23272f;
            border-radius: 20px;
        """)
        layout = QVBoxLayout(dialog)
        label = QLabel("¡Hasta luego!\nDepartamento cerrado correctamente.", dialog)
        label.setStyleSheet("color: white; font-size: 20px; font-weight: bold; padding: 20px;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        dialog.setFixedSize(420, 160)
        QTimer.singleShot(2000, dialog.accept)
        dialog.exec()
        self.setGraphicsEffect(None)
        self.close()
        sys.exit(0)

    def actualizar_reloj_digital(self):
        """Updates the digital clock every second."""
        hora_actual = QTime.currentTime().toString("HH:mm:ss")
        self.lbl_reloj.setText(hora_actual)
        QTimer.singleShot(1000, self.actualizar_reloj_digital)

    def mostrar_dialogo_salones_activos(self):
        """
        Opens the VerSalonesActivosDialog.
        """
        dialog = VerSalonesActivosDialog(self)
        dialog.exec()

if __name__ == "__main__":
    docentes_ejemplo = [
        {"nombre": "Mtro. Juan Pérez"},
        {"nombre": "Dra. Ana López"},
        {"nombre": "Ing. Carlos Ruiz"},
        {"nombre": "Lic. María Torres"}
    ]
    app = QApplication(sys.argv)
    ventana = CentralBienvenida(docentes_ejemplo)
    ventana.showFullScreen()
    sys.exit(app.exec())
