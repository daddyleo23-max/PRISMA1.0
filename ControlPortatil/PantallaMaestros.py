import sys
import json
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialog, QLineEdit, QMessageBox, QGroupBox, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QDateTime, QTime
from PyQt6.QtGui import QColor
from datetime import datetime, timedelta
import random

# --- Definición de la ruta base del proyecto ---
# Asume que PantallaMaestros.py estará en D_S_P/ControlPortatil/
# y los JSONs en D_S_P/
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # D_S_P/ControlPortatil/
PROJECT_ROOT = os.path.join(BASE_DIR, '..') # D_S_P/

# Función auxiliar para obtener la ruta completa de un archivo JSON
def get_json_path(filename):
    return os.path.join(PROJECT_ROOT, filename)

class PantallaMaestros(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pantalla para Maestros (Portátil)")
        self.setGeometry(100, 100, 1200, 700) # Tamaño inicial de la ventana
        self.setStyleSheet("""
            QWidget {
                background-color: #2E3440;
                color: #ECEFF4;
                font-size: 14px;
            }
            QLabel {
                font-size: 16px;
                color: #88C0D0;
            }
            QPushButton {
                background-color: #81A1C1;
                border: none;
                border-radius: 5px;
                padding: 10px;
                min-width: 100px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5E81AC;
            }
            QPushButton#success {
                background-color: #A3BE8C;
                font-weight: bold;
            }
            QPushButton#danger {
                background-color: #BF616A;
                font-weight: bold;
            }
            QTextEdit, QListWidget, QLineEdit {
                background-color: #3B4252;
                border: 1px solid #4C566A;
                border-radius: 5px;
                padding: 8px;
                color: #ECEFF4;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #5E81AC;
            }
            QTableWidget {
                background-color: #3B4252;
                border: 1px solid #4C566A;
                border-radius: 5px;
                color: #ECEFF4;
            }
            QHeaderView::section {
                background-color: #4C566A;
                padding: 5px;
                color: #00e1ff;
                font-weight: bold;
            }
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                border: 2px solid #4C566A;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #00e1ff;
            }
        """)

        self.clase_activa = None
        self.alumnos_clase = []
        self.hora_inicio_clase = None

        self.setup_ui()
        self.cargar_notas_json() # Cargar notas al iniciar

        # Temporizadores para reloj y simulación de asistencia
        self.timer_reloj = QTimer(self)
        self.timer_reloj.timeout.connect(self.actualizar_reloj)
        self.timer_reloj.start(1000) # Actualizar cada segundo

        self.simulacion_timer = QTimer(self)
        self.simulacion_timer.timeout.connect(self.registrar_llegada_simulada)

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- Columna Izquierda: Lista de Notas ---
        left_column = QVBoxLayout()
        notes_list_group = QGroupBox("📝 Notas Guardadas")
        notes_list_layout = QVBoxLayout(notes_list_group)

        self.list_notas = QListWidget()
        self.list_notas.setMinimumWidth(250)
        self.list_notas.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        notes_list_layout.addWidget(self.list_notas)
        notes_list_group.setLayout(notes_list_layout)
        left_column.addWidget(notes_list_group)
        main_layout.addLayout(left_column, 1) # Ocupa 1 parte del espacio

        # --- Columna Central: Área para Escribir Notas ---
        center_column = QVBoxLayout()
        new_note_group = QGroupBox("✍️ Nueva Nota")
        new_note_layout = QVBoxLayout(new_note_group)

        self.input_titulo_nota = QLineEdit()
        self.input_titulo_nota.setPlaceholderText("Título de la nota...")
        new_note_layout.addWidget(QLabel("Título:"))
        new_note_layout.addWidget(self.input_titulo_nota)

        self.text_editor_nota = QTextEdit()
        self.text_editor_nota.setPlaceholderText("Escribe tu nota aquí...")
        new_note_layout.addWidget(QLabel("Contenido:"))
        new_note_layout.addWidget(self.text_editor_nota)

        btn_guardar_nota = QPushButton("Guardar Nota")
        btn_guardar_nota.setObjectName("success")
        btn_guardar_nota.clicked.connect(self.guardar_nota_desde_ui)
        new_note_layout.addWidget(btn_guardar_nota)
        
        new_note_group.setLayout(new_note_layout)
        center_column.addWidget(new_note_group)
        main_layout.addLayout(center_column, 2) # Ocupa 2 partes del espacio

        # --- Columna Derecha: Asistencia y Reloj ---
        right_column = QVBoxLayout()

        # Reloj y detalles de clase
        top_right_layout = QHBoxLayout()
        self.lbl_reloj = QLabel("00:00:00")
        self.lbl_reloj.setStyleSheet("font-size: 32px; font-weight: bold; color: #A3BE8C;")
        self.lbl_reloj.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_detalle_clase = QLabel("Clase no iniciada")
        self.lbl_detalle_clase.setStyleSheet("font-size: 18px; color: #81A1C1;")
        self.lbl_detalle_clase.setAlignment(Qt.AlignmentFlag.AlignRight)

        top_right_layout.addWidget(self.lbl_reloj)
        top_right_layout.addStretch()
        top_right_layout.addWidget(self.lbl_detalle_clase)
        right_column.addLayout(top_right_layout)

        # Tabla de asistencia
        attendance_group = QGroupBox("👥 Asistencia de Alumnos")
        attendance_layout = QVBoxLayout(attendance_group)
        
        self.table_asistencia = QTableWidget()
        self.table_asistencia.setColumnCount(5)
        self.table_asistencia.setHorizontalHeaderLabels(["#", "Nombre", "Núm. Control", "Hora Llegada", "Estado"])
        self.table_asistencia.verticalHeader().setVisible(False)
        self.table_asistencia.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_asistencia.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        attendance_layout.addWidget(self.table_asistencia)
        
        attendance_group.setLayout(attendance_layout)
        right_column.addWidget(attendance_group)

        # Botones de control de clase
        class_control_layout = QHBoxLayout()
        self.btn_iniciar_clase = QPushButton("Iniciar Clase")
        self.btn_iniciar_clase.setObjectName("success")
        self.btn_iniciar_clase.clicked.connect(self.show_seleccionar_clase_dialog)
        
        self.btn_finalizar_clase = QPushButton("Finalizar Clase")
        self.btn_finalizar_clase.setObjectName("danger")
        self.btn_finalizar_clase.setEnabled(False) # Deshabilitado inicialmente
        self.btn_finalizar_clase.clicked.connect(self.finalizar_clase)

        class_control_layout.addWidget(self.btn_iniciar_clase)
        class_control_layout.addWidget(self.btn_finalizar_clase)
        right_column.addLayout(class_control_layout)

        main_layout.addLayout(right_column, 3) # Ocupa 3 partes del espacio

    # --- Métodos de Notas (extraídos y adaptados de dashboard.py) ---
    def guardar_nota_desde_ui(self):
        titulo = self.input_titulo_nota.text().strip()
        texto = self.text_editor_nota.toPlainText().strip()
        if titulo and texto:
            self.guardar_nota_json(titulo, texto)
            self.input_titulo_nota.clear()
            self.text_editor_nota.clear()
            QMessageBox.information(self, "Nota Guardada", "La nota se guardó correctamente.")
        else:
            QMessageBox.warning(self, "Campos Vacíos", "Por favor, escribe un título y una nota antes de guardar.")

    def guardar_nota_json(self, titulo, texto_nota):
        nota = {
            "titulo": titulo,
            "nota": texto_nota,
            "fecha": QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm")
        }
        notas = []
        notas_json_path = get_json_path("notas.json")
        if os.path.exists(notas_json_path):
            with open(notas_json_path, "r", encoding="utf-8") as f:
                try:
                    notas = json.load(f)
                except json.JSONDecodeError:
                    notas = []
        notas.insert(0, nota) # Insertar al inicio (más reciente primero)
        with open(notas_json_path, "w", encoding="utf-8") as f:
            json.dump(notas, f, ensure_ascii=False, indent=2)
        self.cargar_notas_json() # Recargar la lista para mostrar la nueva nota

    def cargar_notas_json(self):
        self.list_notas.clear()
        notas_json_path = get_json_path("notas.json")
        if os.path.exists(notas_json_path):
            with open(notas_json_path, "r", encoding="utf-8") as f:
                try:
                    notas = json.load(f)
                    for nota in notas:
                        # Mostrar título destacado, luego fecha y contenido
                        texto = f"📝 {nota.get('titulo', 'Sin título')}  ({nota.get('fecha', '')})\n{nota.get('nota', '')}"
                        self.list_notas.addItem(texto)
                except json.JSONDecodeError:
                    pass
        else:
            # Crear un archivo notas.json vacío si no existe
            with open(notas_json_path, "w", encoding="utf-8") as f:
                json.dump([], f)


    # --- Métodos de Asistencia (extraídos y adaptados de dashboard.py y SalonView.py) ---
    def actualizar_reloj(self):
        ahora = QDateTime.currentDateTime()
        self.lbl_reloj.setText(ahora.toString("HH:mm:ss"))
        # Si la clase está activa, actualiza los estados de asistencia cada minuto
        if self.clase_activa and ahora.time().second() == 0:
            self.actualizar_estados_asistencia()

    def show_seleccionar_clase_dialog(self):
        dias_trad = {
            "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
            "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
        }
        hoy_en = datetime.now().strftime("%A")
        hoy = dias_trad.get(hoy_en, hoy_en)
        
        clases_disponibles = []
        clases_json_path = get_json_path("clases.json")
        try:
            if os.path.exists(clases_json_path):
                with open(clases_json_path, "r", encoding="utf-8") as f:
                    clases = json.load(f)
                    for clase in clases:
                        # Filtra solo las clases que se imparten hoy
                        if hoy in clase.get("dias", []):
                            clases_disponibles.append(clase)
            else:
                QMessageBox.warning(self, "Advertencia", "El archivo clases.json no se encontró.")
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Error de Archivo", f"El archivo clases.json está dañado o vacío: {e}.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al leer clases.json: {e}")

        dialog = QDialog(self)
        dialog.setWindowTitle("Seleccionar Clase para Asistencia")
        dialog.setStyleSheet("background-color: #23272f; border-radius: 18px;")
        layout = QVBoxLayout(dialog)
        
        lbl_instruccion = QLabel("Clases programadas para hoy:")
        lbl_instruccion.setStyleSheet("color: #00e1ff; font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(lbl_instruccion)

        if not clases_disponibles:
            lbl_empty = QLabel("No hay clases programadas para hoy.")
            lbl_empty.setStyleSheet("color: #ff4d4d; font-size: 18px; font-weight: bold; alignment: center;")
            layout.addWidget(lbl_empty)
            dialog.setFixedSize(400, 150)
            dialog.exec()
            return

        for clase in clases_disponibles:
            btn_clase = QPushButton(
                f"{clase.get('materia', 'N/A')} - Grupo {clase.get('grupo', 'N/A')}\n"
                f"Maestro: {clase.get('docente', 'N/A')}\n"
                f"Horario: {clase.get('hora_inicio', 'N/A')}-{clase.get('hora_fin', 'N/A')}\n"
                f"Salón: {clase.get('salon', 'N/A')}"
            )
            btn_clase.setFixedHeight(100)
            btn_clase.setStyleSheet("""
                QPushButton {
                    background-color: #1e2229;
                    color: #00e1ff;
                    font-size: 18px;
                    border-radius: 14px;
                    font-weight: bold;
                    padding: 10px;
                    margin-bottom: 8px;
                    border: 2px solid #00e1ff;
                }
                QPushButton:hover {
                    background-color: #00b3cc;
                    color: #1e2229;
                }
            """)
            # Usar una lambda para pasar los datos de la clase al iniciar_clase_asistencia
            btn_clase.clicked.connect(lambda _, c=clase: self.iniciar_clase_asistencia(c, dialog))
            layout.addWidget(btn_clase)
        
        dialog.setFixedSize(500, 100 + 110 * len(clases_disponibles)) # Ajustar tamaño dinámicamente
        dialog.exec()

    def iniciar_clase_asistencia(self, clase_data, dialog_parent):
        self.clase_activa = clase_data
        self.hora_inicio_clase = QTime.currentTime() # Usar QTime para la hora de inicio de la clase
        
        self.lbl_detalle_clase.setText(
            f"{self.clase_activa.get('materia', 'N/A')} - {self.clase_activa.get('grupo', 'N/A')} | "
            f"Iniciada: {self.hora_inicio_clase.toString('HH:mm')}"
        )
        
        # Cargar alumnos inscritos en esta clase
        alumnos_todos = []
        alumnos_json_path = get_json_path("alumnos.json")
        if os.path.exists(alumnos_json_path):
            with open(alumnos_json_path, "r", encoding="utf-8") as f:
                try:
                    alumnos_todos = json.load(f)
                except json.JSONDecodeError:
                    alumnos_todos = []
        
        nombre_clase_completo = (
            f"{self.clase_activa.get('materia', 'N/A')} - {self.clase_activa.get('grupo', 'N/A')} "
            f"({self.clase_activa.get('docente', 'N/A')})"
        ).strip()

        self.alumnos_clase = []
        for alumno in alumnos_todos:
            if "clases" in alumno and nombre_clase_completo in alumno["clases"]:
                self.alumnos_clase.append({
                    "nombre": alumno.get("nombre", ""),
                    "numero_control": alumno.get("numero_control", ""),
                    "hora_llegada": None, # Inicialmente sin hora de llegada
                    "estado": "No registrado"
                })
        
        if not self.alumnos_clase:
            QMessageBox.information(self, "Sin Alumnos", f"No hay alumnos registrados para la clase '{nombre_clase_completo}'.")
            self.clase_activa = None
            self.lbl_detalle_clase.setText("Clase no iniciada")
            self.btn_finalizar_clase.setEnabled(False)
            dialog_parent.accept() # Cierra el diálogo de selección de clase
            return

        self.actualizar_tabla_asistencia()
        self.simulacion_timer.start(3000) # Iniciar simulación de llegadas cada 3 segundos
        self.btn_iniciar_clase.setEnabled(False)
        self.btn_finalizar_clase.setEnabled(True)
        dialog_parent.accept() # Cierra el diálogo de selección de clase

    def actualizar_tabla_asistencia(self):
        # Ordenar alumnos: no registrados primero, luego por hora de llegada
        alumnos_ordenados = sorted(
            self.alumnos_clase,
            key=lambda a: (a['hora_llegada'] is None, a['hora_llegada'] or "")
        )

        self.table_asistencia.setRowCount(len(alumnos_ordenados))
        for idx, alumno in enumerate(alumnos_ordenados):
            self.table_asistencia.setItem(idx, 0, QTableWidgetItem(str(idx + 1)))
            self.table_asistencia.setItem(idx, 1, QTableWidgetItem(alumno.get('nombre', '')))
            self.table_asistencia.setItem(idx, 2, QTableWidgetItem(alumno.get('numero_control', '')))
            self.table_asistencia.setItem(idx, 3, QTableWidgetItem(alumno.get('hora_llegada', '--:--:--')))
            
            estado_item = QTableWidgetItem(alumno.get('estado', 'Desconocido'))
            if alumno.get('estado') == "🟢 A tiempo":
                estado_item.setForeground(QColor("#A3BE8C")) # Verde
            elif alumno.get('estado') == "🟡 Retardo moderado":
                estado_item.setForeground(QColor("#EBCB8B")) # Amarillo
            elif alumno.get('estado') == "🔴 Retardo grave":
                estado_item.setForeground(QColor("#BF616A")) # Rojo
            else: # No registrado
                estado_item.setForeground(QColor("#81A1C1")) # Azul claro
            self.table_asistencia.setItem(idx, 4, estado_item)

    def registrar_llegada_simulada(self):
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
                inicio_clase_dt = datetime.combine(datetime.today(), self.hora_inicio_clase.toPyTime())
                llegada_dt = datetime.combine(datetime.today(), hora_actual.toPyTime())
                
                diferencia = llegada_dt - inicio_clase_dt

                if diferencia <= timedelta(minutes=20):
                    alumno["estado"] = "🟢 A tiempo"
                elif diferencia <= timedelta(minutes=60):
                    alumno["estado"] = "🟡 Retardo moderado"
                else:
                    alumno["estado"] = "🔴 Retardo grave"
                
                self.actualizar_tabla_asistencia()
                break # Registrar solo un alumno por tick del timer

        # Detener la simulación si todos los alumnos han llegado
        if all(a["hora_llegada"] is not None for a in self.alumnos_clase):
            self.simulacion_timer.stop()
            QMessageBox.information(self, "Asistencia Completa", "Todos los alumnos han sido registrados.")

    def actualizar_estados_asistencia(self):
        """Actualiza los colores y estados de la tabla de asistencia (cada minuto)"""
        if not self.clase_activa:
            return

        for idx, alumno in enumerate(self.alumnos_clase):
            if alumno["hora_llegada"] is not None:
                hora_llegada_qtime = QTime.fromString(alumno["hora_llegada"], "HH:mm:ss")
                
                # Convertir QTime a datetime.time para cálculos de timedelta
                inicio_clase_dt = datetime.combine(datetime.today(), self.hora_inicio_clase.toPyTime())
                llegada_dt = datetime.combine(datetime.today(), hora_llegada_qtime.toPyTime())
                
                diferencia = llegada_dt - inicio_clase_dt

                estado = ""
                color = QColor()

                if diferencia <= timedelta(minutes=20):
                    estado = "🟢 A tiempo"
                    color = QColor("#A3BE8C") # Verde
                elif diferencia <= timedelta(minutes=60):
                    estado = "🟡 Retardo moderado"
                    color = QColor("#EBCB8B") # Amarillo
                else:
                    estado = "🔴 Retardo grave"
                    color = QColor("#BF616A") # Rojo
                
                alumno["estado"] = estado # Actualizar el estado en los datos
                
                item = self.table_asistencia.item(idx, 4)
                if item:
                    item.setText(estado)
                    item.setForeground(color)

    def finalizar_clase(self):
        if not self.clase_activa:
            QMessageBox.warning(self, "Error", "No hay una clase activa para finalizar.")
            return

        self.simulacion_timer.stop() # Detener la simulación
        
        # Guardar historial (opcional, si quieres que la laptop también guarde historial)
        self.guardar_historial_clase("fin")

        # Mostrar resumen de asistencia
        alumnos_presentes = sum(1 for a in self.alumnos_clase if a["hora_llegada"] is not None)
        total_alumnos = len(self.alumnos_clase)
        
        QMessageBox.information(
            self,
            "Clase Finalizada",
            f"Clase: {self.clase_activa.get('materia', 'N/A')} - {self.clase_activa.get('grupo', 'N/A')}\n"
            f"Asistencia: {alumnos_presentes} de {total_alumnos} alumnos registrados."
        )

        # Resetear estado de la clase
        self.clase_activa = None
        self.alumnos_clase = []
        self.hora_inicio_clase = None
        self.table_asistencia.setRowCount(0) # Limpiar tabla
        self.lbl_detalle_clase.setText("Clase no iniciada")
        self.btn_iniciar_clase.setEnabled(True)
        self.btn_finalizar_clase.setEnabled(False)

    def guardar_historial_clase(self, tipo_evento):
        if not self.clase_activa:
            return

        historial_data = []
        historial_json_path = get_json_path("historial.json")
        if os.path.exists(historial_json_path):
            with open(historial_json_path, "r", encoding="utf-8") as f:
                try:
                    historial_data = json.load(f)
                except json.JSONDecodeError:
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

        with open(historial_json_path, "w", encoding="utf-8") as f:
            json.dump(historial_data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = PantallaMaestros()
    ventana.show()
    sys.exit(app.exec())
