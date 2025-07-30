import sys
import json
import datetime
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QDialog, QListWidget, QMessageBox, QApplication, QTableWidget,
    QTableWidgetItem, QHeaderView, QLineEdit
)
from PyQt6.QtCore import Qt, QTimer, QDateTime, QTime
from PyQt6.QtGui import QColor
from ModoAdmin import ModoAdmin
from OpcionesAdmin import OpcionesAdmin

# --- Definición de la ruta base del proyecto ---
# Esto asume que SalonView.py está en D_S_P/ControlGestion/
# y los JSON están en D_S_P/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(BASE_DIR, '..')

# Función auxiliar para obtener la ruta completa de un archivo JSON
def get_json_path(filename):
    return os.path.join(PROJECT_ROOT, filename)

class HuellaDialog(QDialog):
    """
    Diálogo para simular la verificación de huella dactilar.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Verificación de administrador")
        self.setMinimumSize(500, 300)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(40)

        lbl = QLabel("🔒 Verificación de administrador")
        lbl.setStyleSheet("font-size: 32px; color: #00e1ff; font-weight: bold;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)

        lbl2 = QLabel("Coloca tu huella para acceder a las opciones administrativas")
        lbl2.setStyleSheet("font-size: 22px; color: #A3BE8C;")
        lbl2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl2)

        btn_huella = QPushButton("Simular verificación de huella")
        btn_huella.setStyleSheet("font-size: 22px; padding: 14px;")
        btn_huella.clicked.connect(self.accept)
        layout.addWidget(btn_huella, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet("font-size: 18px; padding: 10px;")
        btn_cancelar.clicked.connect(self.reject)
        layout.addWidget(btn_cancelar, alignment=Qt.AlignmentFlag.AlignCenter)

class SalonView(QWidget):
    """
    Representa la interfaz de la pantalla exterior del salón,
    gestionando el inicio/fin de clases, asistencia y acceso administrativo.
    """
    def __init__(self, nombre_salon, parent=None):
        super().__init__(parent)
        self.nombre_salon = nombre_salon
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.clase_activa = None # Almacena el diccionario de la clase actual
        self.alumnos_clase = [] # Lista de alumnos para la clase activa con su estado de asistencia
        self.hora_inicio_clase_qtime = None # Hora de inicio real de la clase (QTime)

        # Rutas a los archivos JSON para sincronización y datos
        self.estado_clase_path = get_json_path("estado_clase_actual.json")
        self.asistencia_clase_path = get_json_path("asistencia_clase_actual.json")
        self.alumnos_json_path = get_json_path("alumnos.json")
        self.clases_json_path = get_json_path("clases.json")
        self.historial_json_path = get_json_path("historial.json")

        self.setup_ui()
        self.cargar_estado_inicial_salon() # Cargar estado al iniciar

        # Temporizador para la simulación de llegadas de alumnos
        self.simulacion_timer = QTimer(self)
        self.simulacion_timer.timeout.connect(self.registrar_llegada_simulada)

        # Temporizador para la sincronización con estado_clase_actual.json
        self.sincronizacion_timer = QTimer(self)
        self.sincronizacion_timer.timeout.connect(self.sincronizar_estado_clase)
        self.sincronizacion_timer.start(5000) # Chequear cada 5 segundos

    def setup_ui(self):
        """
        Configura la interfaz de usuario principal del SalonView.
        """
        self.setStyleSheet("""
            QWidget {
                background-color: #2E3440;
                color: #ECEFF4;
                font-size: 16px;
            }
            QLabel {
                font-size: 18px;
                color: #81A1C1;
            }
            QPushButton {
                background-color: #00e1ff;
                color: #1e2229;
                font-size: 22px;
                border-radius: 16px;
                font-weight: bold;
                padding: 14px 0;
                min-width: 220px;
                transition: background-color 0.3s;
            }
            QPushButton:hover {
                background-color: #00b3cc;
            }
            QPushButton#admin_button {
                background-color: #3B4252;
                color: #A3BE8C;
                font-size: 16px;
                border-radius: 18px;
                padding: 8px 18px;
                opacity: 0.7;
            }
            QPushButton#admin_button:hover {
                background-color: #23272f;
                color: #00e1ff;
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
            QTableWidget::item {
                padding: 5px;
            }
        """)

        # Limpiar layout existente (si se llama varias veces)
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Header con fecha, hora y nombre del salón
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(20)

        self.lbl_dia = QLabel()
        self.lbl_dia.setStyleSheet("color: #00e1ff; font-size: 22px; font-weight: bold;")
        self.lbl_hora = QLabel()
        self.lbl_hora.setStyleSheet("color: #ffffff; font-size: 32px; font-weight: bold;")
        self.lbl_salon = QLabel(f"Salón: {self.nombre_salon}")
        self.lbl_salon.setStyleSheet("font-size: 28px; font-weight: bold; color: #00e1ff;")

        header_layout.addWidget(self.lbl_dia)
        header_layout.addStretch()
        header_layout.addWidget(self.lbl_hora)
        header_layout.addStretch()
        header_layout.addWidget(self.lbl_salon)
        self.layout.addWidget(header)

        # Temporizador para actualizar fecha y hora
        self.timer_reloj = QTimer(self)
        self.timer_reloj.timeout.connect(self.actualizar_fecha_hora)
        self.timer_reloj.start(1000)
        self.actualizar_fecha_hora()

        # Área central dinámica para menú o clase activa
        self.central_area = QWidget()
        self.central_layout = QVBoxLayout(self.central_area)
        self.central_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.central_layout.setSpacing(30)
        self.layout.addWidget(self.central_area, stretch=1)

        # Botón de Modo Admin (siempre visible en la esquina inferior derecha)
        self.btn_admin = QPushButton("Modo Admin")
        self.btn_admin.setObjectName("admin_button") # Usar objectName para estilo específico
        self.btn_admin.setFixedSize(140, 36)
        self.btn_admin.clicked.connect(self.pedir_huella_para_admin)

        admin_layout = QHBoxLayout()
        admin_layout.addStretch()
        admin_layout.addWidget(self.btn_admin)
        self.layout.addStretch()
        self.layout.addLayout(admin_layout)

    def actualizar_fecha_hora(self):
        """Actualiza la fecha y hora mostradas en el header."""
        ahora = QDateTime.currentDateTime()
        self.lbl_dia.setText(ahora.toString("dddd, dd MMMM yyyy").capitalize())
        self.lbl_hora.setText(ahora.toString("HH:mm:ss"))

    def mostrar_menu_inicial(self):
        """
        Muestra el menú principal con opciones para iniciar clase, abrir/cerrar salón.
        Limpia el área central antes de mostrar el menú.
        """
        print("SalonView: Mostrando menú inicial...")
        self.limpiar_area_central()

        btn_iniciar_clase = QPushButton("🟢 Iniciar Clase")
        btn_abrir_salon = QPushButton("🔓 Abrir Salón")
        btn_cerrar_salon = QPushButton("🔒 Cerrar Salón")

        for btn, color, hover_color in [
            (btn_iniciar_clase, "#00e1ff", "#00b3cc"),
            (btn_abrir_salon, "#00ffb3", "#00cc8a"),
            (btn_cerrar_salon, "#ff4d4d", "#cc0000")
        ]:
            btn.setFixedSize(350, 90)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: #1e2229;
                    font-size: 26px;
                    border-radius: 18px;
                    font-weight: bold;
                    letter-spacing: 1px;
                }}
                QPushButton:hover {{
                    background-color: {hover_color};
                }}
            """)

        btn_iniciar_clase.clicked.connect(self.seleccionar_clase)
        btn_abrir_salon.clicked.connect(self.abrir_salon)
        btn_cerrar_salon.clicked.connect(self.cerrar_salon)

        self.central_layout.addWidget(btn_iniciar_clase)
        self.central_layout.addWidget(btn_abrir_salon)
        self.central_layout.addWidget(btn_cerrar_salon)

    def seleccionar_clase(self):
        """
        Muestra un diálogo para que el profesor seleccione la clase a iniciar.
        Filtra las clases por el día actual y el salón asignado.
        """
        print("SalonView: Iniciando selección de clase...")
        dias_trad = {
            "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
            "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
        }
        hoy_en = datetime.datetime.now().strftime("%A")
        hoy = dias_trad.get(hoy_en, hoy_en)
        clases_hoy = []

        try:
            if os.path.exists(self.clases_json_path):
                with open(self.clases_json_path, "r", encoding="utf-8") as f:
                    clases = json.load(f)
                if not isinstance(clases, list):
                    QMessageBox.warning(self, "Error de Datos", "El contenido de clases.json no es una lista válida.")
                    clases = []
                
                for clase in clases:
                    if hoy in clase.get("dias", []) and clase.get("salon") == self.nombre_salon:
                        clases_hoy.append(clase)
            else:
                QMessageBox.warning(self, "Advertencia", f"El archivo {self.clases_json_path} no se encontró.")
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Error de Archivo", f"El archivo clases.json está dañado o vacío: {e}.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al leer o procesar clases.json: {e}")

        dialog = QDialog(self)
        dialog.setWindowTitle("Selecciona tu clase")
        dialog.setStyleSheet("background-color: #23272f; border-radius: 18px;")
        layout = QVBoxLayout(dialog)
        
        lbl_instruccion = QLabel("Clases programadas para hoy en este salón:")
        lbl_instruccion.setStyleSheet("color: #00e1ff; font-size: 22px; font-weight: bold;")
        layout.addWidget(lbl_instruccion)

        if not clases_hoy:
            lbl_empty = QLabel(f"No hay clases programadas para hoy en el salón {self.nombre_salon}.")
            lbl_empty.setStyleSheet("color: #ff4d4d; font-size: 20px; font-weight: bold;")
            lbl_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(lbl_empty)
            dialog.setFixedSize(500, 200)
            dialog.exec()
            return

        for clase_data in clases_hoy:
            btn = QPushButton(
                f"{clase_data['materia']} - Grupo {clase_data['grupo']}\n"
                f"Horario: {clase_data['hora_inicio']}-{clase_data['hora_fin']}\n"
                f"Maestro: {clase_data['docente']}\n"
                f"Salón: {clase_data['salon']}"
            )
            btn.setFixedHeight(90)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1e2229;
                    color: #00e1ff;
                    font-size: 20px;
                    border-radius: 14px;
                    font-weight: bold;
                    padding: 12px;
                    margin-bottom: 10px;
                    border: 2px solid #00e1ff;
                }
                QPushButton:hover {
                    background-color: #00e1ff;
                    color: #1e2229;
                    border: 2px solid #00e1ff;
                }
            """)
            # Al hacer clic, solo asigna la clase y acepta el diálogo.
            # La lógica de inicio real se ejecuta después de que el diálogo se cierra.
            btn.clicked.connect(lambda _, c=clase_data: (setattr(self, 'clase_activa', c), dialog.accept()))
            layout.addWidget(btn)

        dialog.setFixedSize(500, 80 + 110 * len(clases_hoy))
        result = dialog.exec() # Bloquea hasta que el usuario selecciona o cancela

        if result == QDialog.DialogCode.Accepted and self.clase_activa is not None:
            print("SalonView: Clase seleccionada. Procediendo a pedir huella...")
            self.pedir_huella_y_iniciar_clase()
        else:
            print("SalonView: Selección de clase cancelada o no se seleccionó ninguna.")
            self.clase_activa = None # Asegurarse de que no haya clase activa si se canceló
            self.mostrar_menu_inicial() # Volver al menú principal

    def pedir_huella_y_iniciar_clase(self):
        """
        Solicita la huella del profesor para confirmar el inicio de la clase.
        """
        print("SalonView: Pedir huella e iniciar clase...")
        if self.clase_activa is None:
            self.mostrar_mensaje("Error", "No se ha seleccionado ninguna clase para iniciar.")
            return

        if self.solicitar_huella("Coloca tu huella para iniciar la clase..."):
            print("SalonView: Huella verificada. Iniciando clase activa...")
            self.iniciar_clase_activa()
            self.guardar_historial_clase("inicio")
            self.escribir_estado_clase_actual(True) # Escribir que la clase está activa
        else:
            print("SalonView: Verificación de huella cancelada o fallida. Volviendo al menú inicial.")
            self.clase_activa = None
            self.mostrar_menu_inicial()

    def iniciar_clase_activa(self):
        """
        Configura la interfaz para mostrar la clase activa y la tabla de asistencia.
        Carga los alumnos de la clase y comienza la simulación de llegadas.
        """
        print("SalonView: Mostrando panel de clase activa...")
        self.limpiar_area_central()

        clase = self.clase_activa
        self.hora_inicio_clase_qtime = QTime.currentTime() # Hora real de inicio de la clase

        # Actualizar la etiqueta del salón en el header
        self.lbl_salon.setText(f"Salón: {self.nombre_salon} - Clase Activa")

        lbl_info = QLabel(f"Clase: {clase.get('materia', 'N/A')} - Grupo {clase.get('grupo', 'N/A')}<br>"
                          f"Horario: {clase.get('hora_inicio', 'N/A')}-{clase.get('hora_fin', 'N/A')}<br>"
                          f"Maestro: {clase.get('docente', 'N/A')}")
        lbl_info.setStyleSheet("font-size: 26px; font-weight: bold; color: #A3BE8C; background: #23272f; border-radius: 12px; padding: 18px;")
        lbl_info.setTextFormat(Qt.TextFormat.RichText)
        lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.central_layout.addWidget(lbl_info)

        self.tabla_asistencia = QTableWidget()
        self.tabla_asistencia.setColumnCount(5)
        self.tabla_asistencia.setHorizontalHeaderLabels(["#", "Nombre", "Núm. Control", "Hora Llegada", "Estado"])
        self.tabla_asistencia.verticalHeader().setVisible(False)
        self.tabla_asistencia.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_asistencia.setStyleSheet("""
            QTableWidget {
                background-color: #3B4252;
                border: 1px solid #4C566A;
                border-radius: 5px;
                font-size: 20px;
                color: #ECEFF4;
            }
            QHeaderView::section {
                background-color: #4C566A;
                color: #00e1ff;
                padding: 8px;
                font-size: 20px;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        self.tabla_asistencia.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_asistencia.verticalHeader().setDefaultSectionSize(48)
        self.central_layout.addWidget(self.tabla_asistencia)

        # Cargar alumnos inscritos en esta clase
        self.alumnos_clase = []
        todos_los_alumnos = []
        try:
            if os.path.exists(self.alumnos_json_path):
                with open(self.alumnos_json_path, "r", encoding="utf-8") as f:
                    todos_los_alumnos = json.load(f)
            else:
                QMessageBox.warning(self, "Advertencia", f"El archivo {self.alumnos_json_path} no se encontró. No se pudieron cargar los alumnos.")
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Error de Archivo", f"El archivo alumnos.json está dañado o vacío: {e}. No se pudieron cargar los alumnos.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error inesperado al leer alumnos.json: {e}")

        nombre_clase_completo_para_filtrar = (
            f"{clase.get('materia', 'N/A')} - {clase.get('grupo', 'N/A')} "
            f"({clase.get('docente', 'N/A')})"
        ).strip()

        for alumno in todos_los_alumnos:
            if "clases" in alumno and nombre_clase_completo_para_filtrar in alumno["clases"]:
                self.alumnos_clase.append({
                    "nombre": alumno.get("nombre", ""),
                    "numero_control": alumno.get("numero_control", ""),
                    "hora_llegada": None,
                    "estado": "No registrado"
                })
        
        if not self.alumnos_clase:
            QMessageBox.information(self, "Información", "No hay alumnos inscritos en esta clase. Puedes registrarlos en la sección de 'Registrar Alumnos'.")
            self.clase_activa = None
            self.lbl_salon.setText(f"Salón: {self.nombre_salon}") # Resetear etiqueta
            self.mostrar_menu_inicial()
            return
        
        self.actualizar_tabla_asistencia()
        self.escribir_asistencia_clase_actual() # Guardar estado inicial de asistencia

        self.simulacion_timer.start(3000) # Iniciar simulación de llegadas

        # Botones de control de clase
        btn_terminar = QPushButton("Terminar Clase")
        btn_terminar.setFixedHeight(60)
        btn_terminar.setFixedWidth(320)
        btn_terminar.setStyleSheet("""
            QPushButton {
                font-size: 22px;
                background-color: #ff4d4d;
                color: #1e2229;
                border-radius: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
        """)
        btn_terminar.clicked.connect(self.verificar_huella_y_mostrar_resumen)
        self.central_layout.addWidget(btn_terminar, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_registro_manual = QPushButton("Registro Manual")
        btn_registro_manual.setFixedHeight(60)
        btn_registro_manual.setFixedWidth(320)
        btn_registro_manual.setStyleSheet("""
            QPushButton {
                font-size: 22px;
                background-color: #00ffb3;
                color: #1e2229;
                border-radius: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00cc8a;
            }
        """)
        btn_registro_manual.clicked.connect(self.mostrar_dialogo_registro_manual)
        self.central_layout.addWidget(btn_registro_manual, alignment=Qt.AlignmentFlag.AlignCenter)

    def actualizar_tabla_asistencia(self):
        """
        Actualiza la QTableWidget de asistencia con los datos de self.alumnos_clase.
        """
        self.tabla_asistencia.setRowCount(len(self.alumnos_clase))
        for idx, alumno in enumerate(self.alumnos_clase):
            self.tabla_asistencia.setItem(idx, 0, QTableWidgetItem(str(idx + 1)))
            self.tabla_asistencia.setItem(idx, 1, QTableWidgetItem(alumno.get('nombre', '')))
            self.tabla_asistencia.setItem(idx, 2, QTableWidgetItem(alumno.get('numero_control', '')))
            self.tabla_asistencia.setItem(idx, 3, QTableWidgetItem(alumno.get('hora_llegada', '--:--:--')))
            
            estado_item = QTableWidgetItem(alumno.get('estado', 'Desconocido'))
            if alumno.get('estado') == "🟢 A tiempo":
                estado_item.setForeground(QColor("#00ffb3"))
            elif alumno.get('estado') == "🟡 Retardo moderado":
                estado_item.setForeground(QColor("#EBCB8B")) # Amarillo
            elif alumno.get('estado') == "🔴 Retardo grave":
                estado_item.setForeground(QColor("#BF616A")) # Rojo
            else: # No registrado
                estado_item.setForeground(QColor("#ECEFF4")) # Blanco/gris claro
            self.tabla_asistencia.setItem(idx, 4, estado_item)

    def registrar_llegada_simulada(self):
        """
        Simula la llegada de un alumno y actualiza su estado.
        """
        if not self.clase_activa:
            self.simulacion_timer.stop()
            return

        # Buscar el primer alumno que no ha llegado
        for alumno in self.alumnos_clase:
            if alumno["hora_llegada"] is None:
                hora_actual = QTime.currentTime()
                hora_llegada_str = hora_actual.toString("HH:mm:ss")
                alumno["hora_llegada"] = hora_llegada_str

                # Calcular el estado de asistencia
                # Convertir QTime a datetime.time para cálculos de timedelta
                # Asegurarse de que hora_inicio_clase_qtime no sea None
                if self.hora_inicio_clase_qtime:
                    inicio_clase_dt = datetime.datetime.combine(datetime.date.today(), self.hora_inicio_clase_qtime.toPyTime())
                    llegada_dt = datetime.datetime.combine(datetime.date.today(), hora_actual.toPyTime())
                    diferencia = llegada_dt - inicio_clase_dt

                    if diferencia <= datetime.timedelta(minutes=20):
                        alumno["estado"] = "🟢 A tiempo"
                    elif diferencia <= datetime.timedelta(minutes=60):
                        alumno["estado"] = "🟡 Retardo moderado"
                    else:
                        alumno["estado"] = "🔴 Retardo grave"
                else:
                    alumno["estado"] = "Registrado (hora de inicio no definida)" # Fallback

                self.actualizar_tabla_asistencia()
                self.escribir_asistencia_clase_actual() # Sincronizar asistencia
                break # Registrar solo un alumno por tick del timer

        # Detener la simulación si todos los alumnos han llegado
        if all(a["hora_llegada"] is not None for a in self.alumnos_clase):
            self.simulacion_timer.stop()
            self.mostrar_mensaje("Asistencia Completa", "Todos los alumnos han sido registrados.")

    def mostrar_dialogo_registro_manual(self):
        """
        Muestra un diálogo para registrar manualmente la asistencia de un alumno.
        """
        if not self.clase_activa:
            self.mostrar_mensaje("Error", "No hay una clase activa para registrar asistencia manualmente.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Registro Manual de Asistencia")
        dialog.setStyleSheet("background-color: #23272f; border-radius: 18px;")
        layout = QVBoxLayout(dialog)

        lbl_instruccion = QLabel("Ingresa el número de control del alumno:")
        lbl_instruccion.setStyleSheet("color: #ECEFF4; font-size: 18px; margin-bottom: 10px;")
        layout.addWidget(lbl_instruccion)

        input_control = QLineEdit()
        input_control.setPlaceholderText("Número de control")
        input_control.setStyleSheet("""
            QLineEdit {
                background: #2E3440; color: #00e1ff; font-size: 20px;
                border: 2px solid #00e1ff; border-radius: 10px; padding: 10px;
            }
        """)
        layout.addWidget(input_control)

        btn_registrar = QPushButton("Registrar")
        btn_registrar.setStyleSheet("""
            QPushButton {
                background-color: #00e1ff; color: #1e2229; font-size: 20px;
                border-radius: 14px; font-weight: bold; padding: 12px;
            }
            QPushButton:hover {
                background-color: #00b3cc;
            }
        """)
        btn_registrar.clicked.connect(lambda: self.registrar_asistencia_manual(input_control.text().strip(), dialog))
        layout.addWidget(btn_registrar)

        dialog.setFixedSize(400, 250)
        dialog.exec()

    def registrar_asistencia_manual(self, numero_control, dialog):
        """
        Procesa el registro manual de asistencia para un alumno.
        """
        if not numero_control:
            QMessageBox.warning(dialog, "Error", "Por favor, ingresa un número de control.")
            return

        alumno_encontrado = False
        for alumno in self.alumnos_clase:
            if alumno.get("numero_control") == numero_control:
                if alumno["hora_llegada"] is None:
                    hora_actual = QTime.currentTime()
                    hora_llegada_str = hora_actual.toString("HH:mm:ss")
                    alumno["hora_llegada"] = hora_llegada_str

                    if self.hora_inicio_clase_qtime:
                        inicio_clase_dt = datetime.datetime.combine(datetime.date.today(), self.hora_inicio_clase_qtime.toPyTime())
                        llegada_dt = datetime.datetime.combine(datetime.date.today(), hora_actual.toPyTime())
                        diferencia = llegada_dt - inicio_clase_dt

                        if diferencia <= datetime.timedelta(minutes=20):
                            alumno["estado"] = "🟢 A tiempo"
                        elif diferencia <= datetime.timedelta(minutes=60):
                            alumno["estado"] = "🟡 Retardo moderado"
                        else:
                            alumno["estado"] = "🔴 Retardo grave"
                    else:
                        alumno["estado"] = "Registrado (hora de inicio no definida)"

                    self.actualizar_tabla_asistencia()
                    self.escribir_asistencia_clase_actual() # Sincronizar asistencia
                    QMessageBox.information(dialog, "Éxito", f"Asistencia registrada para {alumno['nombre']}.")
                else:
                    QMessageBox.information(dialog, "Información", f"{alumno['nombre']} ya ha sido registrado.")
                alumno_encontrado = True
                break
        
        if not alumno_encontrado:
            QMessageBox.warning(dialog, "Error", "Número de control no encontrado para esta clase.")
        
        dialog.accept() # Cerrar el diálogo después de procesar

    def verificar_huella_y_mostrar_resumen(self):
        """
        Solicita la huella para terminar la clase y muestra un resumen.
        """
        print("SalonView: Verificando huella para terminar clase...")
        if self.solicitar_huella("Coloca tu huella para terminar la clase..."):
            print("SalonView: Huella verificada. Mostrando resumen y finalizando clase...")
            self.mostrar_resumen_clase()
            self.guardar_historial_clase("fin")
            self.escribir_estado_clase_actual(False) # Marcar clase como inactiva
        else:
            print("SalonView: Verificación de huella para terminar clase cancelada.")

    def mostrar_resumen_clase(self):
        """
        Muestra un resumen de la asistencia al finalizar la clase.
        """
        print("SalonView: Mostrando resumen de clase...")
        self.simulacion_timer.stop()

        clase = self.clase_activa
        alumnos_asistentes = sum(1 for a in self.alumnos_clase if a['hora_llegada'])

        dialog = QDialog(self)
        dialog.setWindowTitle("Resumen de la Clase")
        dialog.setStyleSheet("background-color: #23272f; border-radius: 18px;")
        layout = QVBoxLayout(dialog)
        resumen = QLabel(
            f"<b>Clase:</b> {clase.get('materia', 'N/A')} - Grupo {clase.get('grupo', 'N/A')}<br>"
            f"<b>Horario:</b> {clase.get('hora_inicio', 'N/A')}-{clase.get('hora_fin', 'N/A')}<br>"
            f"<b>Maestro:</b> {clase.get('docente', 'N/A')}<br><br>"
            f"<b>Alumnos registrados:</b> {alumnos_asistentes} / {len(self.alumnos_clase)}"
        )
        resumen.setStyleSheet("color: #00e1ff; font-size: 20px; font-weight: bold; padding: 18px;")
        resumen.setTextFormat(Qt.TextFormat.RichText)
        resumen.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(resumen)

        btn_salir = QPushButton("Salir y Cerrar Salón")
        btn_salir.setFixedHeight(50)
        btn_salir.setFixedWidth(260)
        btn_salir.setStyleSheet("""
            QPushButton {
                background-color: #00e1ff;
                color: #1e2229;
                font-size: 20px;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00b3cc;
            }
        """)
        btn_salir.clicked.connect(lambda: (dialog.accept(), self.cerrar_salon(solicitar_huella=False)))
        layout.addWidget(btn_salir, alignment=Qt.AlignmentFlag.AlignCenter)
        dialog.setFixedSize(480, 320)
        dialog.exec()
        print("SalonView: Resumen de clase mostrado y diálogo cerrado.")

    def guardar_historial_clase(self, tipo_evento):
        """
        Guarda el registro de inicio o fin de una clase en historial.json.
        """
        if not self.clase_activa:
            print(f"Advertencia: No hay clase activa para guardar evento '{tipo_evento}' en historial.")
            return

        historial_data = []
        try:
            if os.path.exists(self.historial_json_path):
                with open(self.historial_json_path, "r", encoding="utf-8") as f:
                    historial_data = json.load(f)
            else:
                # Crear archivo vacío si no existe
                with open(self.historial_json_path, "w", encoding="utf-8") as f:
                    json.dump([], f)
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Error de Archivo", f"El archivo historial.json está dañado o vacío: {e}.")
            historial_data = []
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error inesperado al leer historial.json: {e}")
            historial_data = []

        registro = {
            "fecha": QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss"),
            "tipo_evento": tipo_evento,
            "materia": self.clase_activa.get("materia", "N/A"),
            "grupo": self.clase_activa.get("grupo", "N/A"),
            "docente": self.clase_activa.get("docente", "N/A"),
            "salon": self.clase_activa.get("salon", "N/A"),
            "alumnos": [
                {
                    "nombre": a.get("nombre", ""),
                    "numero_control": a.get("numero_control", ""),
                    "hora_llegada": a.get("hora_llegada", "N/A"),
                    "estado": a.get("estado", "N/A")
                } for a in self.alumnos_clase
            ]
        }
        historial_data.append(registro)

        try:
            with open(self.historial_json_path, "w", encoding="utf-8") as f:
                json.dump(historial_data, f, ensure_ascii=False, indent=2)
            print(f"SalonView: Evento de clase '{tipo_evento}' guardado en historial.json.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el historial de la clase: {e}")

    def escribir_estado_clase_actual(self, activa):
        """
        Escribe el estado actual de la clase (activa/inactiva) en estado_clase_actual.json.
        """
        estado = {
            "activa": activa,
            "materia": self.clase_activa.get("materia", "") if self.clase_activa else "",
            "grupo": self.clase_activa.get("grupo", "") if self.clase_activa else "",
            "docente": self.clase_activa.get("docente", "") if self.clase_activa else "",
            "salon": self.nombre_salon,
            "hora_inicio_real": self.hora_inicio_clase_qtime.toString("HH:mm:ss") if self.hora_inicio_clase_qtime else ""
        }
        try:
            with open(self.estado_clase_path, "w", encoding="utf-8") as f:
                json.dump(estado, f, ensure_ascii=False, indent=2)
            print(f"SalonView: Estado de clase actual escrito: activa={activa}")
        except Exception as e:
            QMessageBox.critical(self, "Error de Sincronización", f"No se pudo escribir estado_clase_actual.json: {e}")

    def escribir_asistencia_clase_actual(self):
        """
        Escribe el estado actual de la asistencia de los alumnos en asistencia_clase_actual.json.
        """
        try:
            with open(self.asistencia_clase_path, "w", encoding="utf-8") as f:
                json.dump(self.alumnos_clase, f, ensure_ascii=False, indent=2)
            print("SalonView: Asistencia de clase actual escrita.")
        except Exception as e:
            QMessageBox.critical(self, "Error de Sincronización", f"No se pudo escribir asistencia_clase_actual.json: {e}")

    def cargar_estado_inicial_salon(self):
        """
        Carga el estado de la clase al iniciar el SalonView,
        para saber si una clase ya estaba activa (ej. iniciada por la laptop).
        """
        print("SalonView: Cargando estado inicial del salón...")
        try:
            if os.path.exists(self.estado_clase_path):
                with open(self.estado_clase_path, "r", encoding="utf-8") as f:
                    estado = json.load(f)
                
                if estado.get("activa") and estado.get("salon") == self.nombre_salon:
                    self.clase_activa = {
                        "materia": estado.get("materia"),
                        "grupo": estado.get("grupo"),
                        "docente": estado.get("docente"),
                        "salon": estado.get("salon"),
                        "hora_inicio": estado.get("hora_inicio_real", "00:00:00") # Usar para mostrar
                    }
                    self.hora_inicio_clase_qtime = QTime.fromString(estado.get("hora_inicio_real", "00:00:00"), "HH:mm:ss")
                    
                    # Cargar asistencia actual
                    if os.path.exists(self.asistencia_clase_path):
                        with open(self.asistencia_clase_path, "r", encoding="utf-8") as f_asistencia:
                            self.alumnos_clase = json.load(f_asistencia)
                        print("SalonView: Asistencia inicial cargada.")
                    
                    print("SalonView: Clase activa detectada al inicio. Restaurando interfaz...")
                    self.iniciar_clase_activa() # Re-mostrar la interfaz de clase activa
                else:
                    print("SalonView: No hay clase activa registrada para este salón.")
                    self.mostrar_menu_inicial()
            else:
                print("SalonView: estado_clase_actual.json no encontrado. Iniciando menú principal.")
                self.escribir_estado_clase_actual(False) # Crear archivo con estado inactivo
                self.mostrar_menu_inicial()
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Error de Sincronización", f"El archivo estado_clase_actual.json está dañado o vacío: {e}. Iniciando menú principal.")
            self.mostrar_menu_inicial()
        except Exception as e:
            QMessageBox.critical(self, "Error de Carga", f"Ocurrió un error al cargar el estado inicial del salón: {e}. Iniciando menú principal.")
            self.mostrar_menu_inicial()
    
    def sincronizar_estado_clase(self):
        """
        Lee periódicamente estado_clase_actual.json para sincronizar el estado
        de la clase con otros dispositivos (ej. Pantalla Maestros).
        """
        # print("SalonView: Sincronizando estado de clase...")
        try:
            if os.path.exists(self.estado_clase_path):
                with open(self.estado_clase_path, "r", encoding="utf-8") as f:
                    estado_remoto = json.load(f)
                
                # Si la clase está activa en el archivo y no localmente, iniciarla
                if estado_remoto.get("activa") and estado_remoto.get("salon") == self.nombre_salon and self.clase_activa is None:
                    print("SalonView: Detectada clase activa iniciada externamente. Restaurando...")
                    self.clase_activa = {
                        "materia": estado_remoto.get("materia"),
                        "grupo": estado_remoto.get("grupo"),
                        "docente": estado_remoto.get("docente"),
                        "salon": estado_remoto.get("salon"),
                        "hora_inicio": estado_remoto.get("hora_inicio_real", "00:00:00")
                    }
                    self.hora_inicio_clase_qtime = QTime.fromString(estado_remoto.get("hora_inicio_real", "00:00:00"), "HH:mm:ss")
                    
                    # Cargar asistencia actual desde el archivo de asistencia
                    if os.path.exists(self.asistencia_clase_path):
                        with open(self.asistencia_clase_path, "r", encoding="utf-8") as f_asistencia:
                            self.alumnos_clase = json.load(f_asistencia)
                    
                    self.iniciar_clase_activa() # Re-mostrar la interfaz de clase activa
                    self.simulacion_timer.stop() # Detener simulación si ya se está registrando externamente

                # Si la clase está inactiva en el archivo pero activa localmente, finalizarla
                elif not estado_remoto.get("activa") and self.clase_activa is not None and estado_remoto.get("salon") == self.nombre_salon:
                    print("SalonView: Detectada clase finalizada externamente. Finalizando localmente...")
                    self.finalizar_clase_sin_huella() # Nuevo método para finalizar sin pedir huella
                
                # Si la clase está activa y ya la tenemos activa, solo actualizar asistencia
                elif estado_remoto.get("activa") and self.clase_activa is not None and estado_remoto.get("salon") == self.nombre_salon:
                    if os.path.exists(self.asistencia_clase_path):
                        with open(self.asistencia_clase_path, "r", encoding="utf-8") as f_asistencia:
                            asistencia_remota = json.load(f_asistencia)
                        
                        # Actualizar self.alumnos_clase con los datos más recientes
                        # Esto es una fusión simple, podrías necesitar una lógica más compleja
                        # si los alumnos pueden ser añadidos/removidos en tiempo real.
                        for remote_alumno in asistencia_remota:
                            found = False
                            for local_alumno in self.alumnos_clase:
                                if local_alumno.get("numero_control") == remote_alumno.get("numero_control"):
                                    local_alumno["hora_llegada"] = remote_alumno.get("hora_llegada")
                                    local_alumno["estado"] = remote_alumno.get("estado")
                                    found = True
                                    break
                            if not found: # Si el alumno remoto no está en nuestra lista, añadirlo
                                self.alumnos_clase.append(remote_alumno)
                        
                        self.actualizar_tabla_asistencia()
                        # print("SalonView: Asistencia actualizada desde archivo externo.")

        except json.JSONDecodeError as e:
            print(f"SalonView: Error al leer estado_clase_actual.json o asistencia_clase_actual.json (dañado/vacío): {e}")
        except Exception as e:
            print(f"SalonView: Error inesperado durante la sincronización: {e}")

    def finalizar_clase_sin_huella(self):
        """
        Finaliza la clase sin pedir verificación de huella.
        Usado para sincronización cuando la clase se termina desde otro dispositivo.
        """
        print("SalonView: Finalizando clase localmente (sin huella) por sincronización externa.")
        if not self.clase_activa:
            return

        self.simulacion_timer.stop()
        self.guardar_historial_clase("fin") # Guardar el historial final
        
        # Resetear estado local
        self.clase_activa = None
        self.alumnos_clase = []
        self.hora_inicio_clase_qtime = None
        
        # Limpiar archivos de estado temporal
        if os.path.exists(self.estado_clase_path):
            try:
                os.remove(self.estado_clase_path)
                print(f"SalonView: {self.estado_clase_path} eliminado.")
            except Exception as e:
                print(f"SalonView: Error al eliminar {self.estado_clase_path}: {e}")
        if os.path.exists(self.asistencia_clase_path):
            try:
                os.remove(self.asistencia_clase_path)
                print(f"SalonView: {self.asistencia_clase_path} eliminado.")
            except Exception as e:
                print(f"SalonView: Error al eliminar {self.asistencia_clase_path}: {e}")

        self.lbl_salon.setText(f"Salón: {self.nombre_salon}") # Resetear etiqueta
        self.mostrar_menu_inicial() # Volver al menú principal

    def abrir_salon(self):
        """Abre el salón (simulado) con verificación de huella."""
        if self.solicitar_huella("Coloca tu huella para abrir el salón..."):
            self.mostrar_mensaje("Salón abierto", "¡Salón abierto correctamente!")

    def cerrar_salon(self, solicitar_huella=True):
        """
        Cierra el salón (simulado) con verificación de huella.
        También finaliza la clase activa si la hay.
        """
        print("SalonView: Intentando cerrar salón...")
        if not solicitar_huella or self.solicitar_huella("Coloca tu huella para cerrar el salón..."):
            if self.clase_activa:
                print("SalonView: Clase activa detectada al cerrar salón. Finalizando clase...")
                self.finalizar_clase_sin_huella() # Finalizar clase antes de cerrar salón
            
            self.mostrar_mensaje("Salón cerrado", "¡Salón cerrado correctamente!")
            self.clase_activa = None
            self.alumnos_clase = []
            self.simulacion_timer.stop()
            
            # Asegurarse de que el archivo de estado esté inactivo al cerrar el salón
            self.escribir_estado_clase_actual(False) 
            
            self.mostrar_menu_inicial()
            print("SalonView: Salón cerrado. Estado de clase y alumnos reseteado.")

    def solicitar_huella(self, mensaje):
        """
        Muestra un diálogo para simular la solicitud de huella dactilar.
        Retorna True si la huella es "correcta" (botón Aceptar), False si se cancela.
        """
        print(f"SalonView: Solicitando huella: {mensaje}")
        dialog = QDialog(self)
        dialog.setWindowTitle("Verificación de Huella")
        dialog.setStyleSheet("background-color: #23272f; border-radius: 18px;")
        layout = QVBoxLayout(dialog)
        label = QLabel(mensaje)
        label.setStyleSheet("color: white; font-size: 20px; font-weight: bold; padding: 20px;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        btn_ok = QPushButton("Simular Huella Correcta")
        btn_ok.setFixedHeight(50)
        btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #00e1ff;
                color: #1e2229;
                font-size: 18px;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00b3cc;
            }
        """)
        btn_ok.clicked.connect(dialog.accept)
        layout.addWidget(btn_ok)
        dialog.setFixedSize(420, 180)
        result = dialog.exec()
        return result == QDialog.DialogCode.Accepted

    def mostrar_mensaje(self, titulo, mensaje):
        """
        Muestra un cuadro de mensaje simple.
        """
        print(f"SalonView: Mostrando mensaje: {titulo} - {mensaje}")
        dialog = QDialog(self)
        dialog.setWindowTitle(titulo)
        dialog.setStyleSheet("background-color: #23272f; border-radius: 18px;")
        layout = QVBoxLayout(dialog)
        label = QLabel(mensaje)
        label.setStyleSheet("color: #00e1ff; font-size: 22px; font-weight: bold; padding: 20px;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        btn_ok = QPushButton("Aceptar")
        btn_ok.setFixedHeight(50)
        btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #00e1ff;
                color: #1e2229;
                font-size: 18px;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00b3cc;
            }
        """)
        btn_ok.clicked.connect(dialog.accept)
        layout.addWidget(btn_ok)
        dialog.setFixedSize(420, 160)
        dialog.exec()

    def pedir_huella_para_admin(self):
        """
        Solicita la huella para acceder al modo administrador.
        """
        print("SalonView: Solicitando huella para admin...")
        dialog = HuellaDialog(self)
        if dialog.exec():
            self.mostrar_opciones_admin()
            print("SalonView: Acceso de admin concedido.")
        else:
            print("SalonView: Acceso de admin denegado.")

    def verificar_huella_admin(self):
        """
        Simula la verificación de huella de administrador.
        """
        print("SalonView: Verificando huella de admin (simulado)...")
        self.mostrar_opciones_admin()

    def mostrar_opciones_admin(self):
        """
        Muestra el panel de opciones administrativas.
        """
        print("SalonView: Mostrando opciones de admin...")
        self.limpiar_area_central()
        opciones_admin = OpcionesAdmin(self, salir_callback=self.mostrar_menu_inicial)
        self.central_layout.addWidget(opciones_admin)

    def limpiar_area_central(self):
        """
        Limpia todos los widgets del layout central dinámico.
        """
        print("SalonView: Limpiando área central...")
        for i in reversed(range(self.central_layout.count())):
            widget = self.central_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        print("SalonView: Área central limpiada.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Puedes pasar el nombre del salón como argumento o predefinirlo
    # Por ejemplo, si el salón es "Y9":
    ventana = SalonView("Y9")
    ventana.showMaximized()
    sys.exit(app.exec())
