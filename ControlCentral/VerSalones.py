from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QHBoxLayout,
    QSizePolicy, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView, QApplication # Añadidos para la tabla
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer, QTime # Añadido QTime para manejo de horas
import json
import os
from datetime import datetime, time as dt_time # Importar datetime y time
import sys

# --- Definición de la ruta base del proyecto ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(BASE_DIR, '..')

# Función auxiliar para obtener la ruta completa de un archivo JSON
def get_json_path(filename):
    return os.path.join(PROJECT_ROOT, filename)

class VerSalones(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget {
                background-color: #23272f;
                border-radius: 18px; /* Aplicar un borde redondeado a la ventana principal */
            }
            QLabel#titulo {
                color: #00e1ff;
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 18px;
            }
            QLabel {
                color: #A3BE8C;
                font-size: 19px;
                font-weight: bold;
                margin-bottom: 2px;
            }
            QPushButton {
                background-color: #00e1ff;
                color: #1e2229;
                font-size: 18px;
                border-radius: 12px;
                font-weight: bold;
                padding: 10px 0;
                min-width: 120px;
                transition: background-color 0.3s;
            }
            QPushButton:hover {
                background-color: #00b3cc;
            }
            QPushButton.ocupado {
                background-color: #BF616A; /* Rojo para salones ocupados */
                color: #23272f;
            }
            QPushButton.ocupado:hover {
                background-color: #a94f55;
            }
            QTableWidget {
                background-color: #3B4252;
                border: 1px solid #4C566A;
                border-radius: 8px;
                font-size: 16px;
                color: #ECEFF4;
                selection-background-color: #00e1ff;
                selection-color: #1e2229;
            }
            QHeaderView::section {
                background-color: #4C566A;
                color: #00e1ff;
                font-size: 16px;
                font-weight: bold;
                padding: 8px;
                border: none;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(25) # Aumentar espaciado general

        lbl_titulo = QLabel("Gestión de Salones")
        lbl_titulo.setObjectName("titulo")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(lbl_titulo)

        # --- Sección de Salones por Piso (Grid Layout) ---
        lbl_salones_disponibles = QLabel("Salones Disponibles/Ocupados:")
        lbl_salones_disponibles.setStyleSheet("font-size: 22px; color: #00e1ff; font-weight: bold; margin-bottom: 10px;")
        self.layout.addWidget(lbl_salones_disponibles)

        self.grid_layout_salones = QGridLayout()
        self.grid_layout_salones.setSpacing(15) # Espaciado entre botones de salón
        self.layout.addLayout(self.grid_layout_salones)

        self.cargar_salones() # Carga los botones de salones

        # --- Sección de Clases Activas Ahora (Tabla) ---
        lbl_clases_activas = QLabel("Clases Activas Ahora:")
        lbl_clases_activas.setStyleSheet("font-size: 22px; color: #00e1ff; font-weight: bold; margin-top: 30px; margin-bottom: 10px;")
        self.layout.addWidget(lbl_clases_activas)

        self.tabla_clases_activas = QTableWidget()
        self.tabla_clases_activas.setColumnCount(6)
        self.tabla_clases_activas.setHorizontalHeaderLabels(["Materia", "Grupo", "Docente", "Salón", "Hora Inicio", "Hora Fin"])
        self.tabla_clases_activas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_clases_activas.verticalHeader().setVisible(False)
        self.tabla_clases_activas.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # No editable
        self.layout.addWidget(self.tabla_clases_activas)

        # Timer para actualizar las clases activas
        self.timer_clases_activas = QTimer(self)
        self.timer_clases_activas.timeout.connect(self.cargar_clases_activas)
        self.timer_clases_activas.start(60000) # Actualizar cada 60 segundos (1 minuto)

        self.cargar_clases_activas() # Cargar clases activas al inicio

        self.layout.addStretch() # Empuja todo el contenido hacia arriba

    def cargar_salones(self):
        """Carga los salones desde Salones.json y crea botones."""
        # Limpiar botones existentes
        for i in reversed(range(self.grid_layout_salones.count())):
            widget = self.grid_layout_salones.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        salones_path = get_json_path("Salones.json")
        salones = []
        try:
            if os.path.exists(salones_path):
                with open(salones_path, "r", encoding="utf-8") as f:
                    salones = json.load(f)
            else:
                QMessageBox.warning(self, "Advertencia", f"El archivo Salones.json no se encontró en {salones_path}. No se pudieron cargar los salones.")
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Error de Archivo", "El archivo Salones.json está dañado o vacío. No se pudieron cargar los salones.")
        except Exception as e:
            QMessageBox.critical(self, "Error de Carga", f"Ocurrió un error inesperado al cargar Salones.json: {e}.")

        # Crear botones de salón y añadirlos al grid
        row, col = 0, 0
        for salon in salones:
            nombre_salon = salon.get("nombre", "N/A")
            estado = salon.get("estado", "libre") # 'libre' o 'ocupado'
            
            btn_salon = QPushButton(nombre_salon)
            btn_salon.setFixedSize(150, 80) # Tamaño fijo para los botones de salón
            
            if estado == "ocupado":
                btn_salon.setProperty("class", "ocupado") # Usar property para CSS
                btn_salon.setToolTip(f"Salón {nombre_salon} ocupado.")
            else:
                btn_salon.setProperty("class", "") # Limpiar propiedad si no está ocupado
                btn_salon.setToolTip(f"Salón {nombre_salon} libre.")
            
            btn_salon.clicked.connect(lambda checked, s=salon: self.mostrar_info_salon(s))
            self.grid_layout_salones.addWidget(btn_salon, row, col)
            
            col += 1
            if col > 4: # 5 columnas por fila
                col = 0
                row += 1

    def mostrar_info_salon(self, salon):
        """Muestra información detallada de un salón al hacer clic."""
        nombre_salon = salon.get("nombre", "Sin nombre")
        estado = salon.get("estado", "libre")
        clase_actual = salon.get("clase", "N/A")
        horario_actual = salon.get("horario", "N/A")

        info_msg = f"<b>Salón:</b> {nombre_salon}<br>" \
                   f"<b>Estado:</b> {'Ocupado' if estado == 'ocupado' else 'Libre'}<br>"
        
        if estado == "ocupado":
            info_msg += f"<b>Clase Actual:</b> {clase_actual}<br>" \
                        f"<b>Horario:</b> {horario_actual}"
        
        QMessageBox.information(self, "Información del Salón", info_msg)

    def cargar_clases_activas(self):
        """
        Carga y muestra las clases que están activas en el momento actual.
        """
        self.tabla_clases_activas.setRowCount(0) # Limpiar tabla
        
        clases_path = get_json_path("clases.json")
        clases = []
        try:
            if os.path.exists(clases_path):
                with open(clases_path, "r", encoding="utf-8") as f:
                    clases = json.load(f)
            else:
                self.tabla_clases_activas.setRowCount(1)
                self.tabla_clases_activas.setItem(0, 0, QTableWidgetItem("Archivo clases.json no encontrado."))
                self.tabla_clases_activas.setSpan(0, 0, 1, 6) # Unir celdas
                return
        except json.JSONDecodeError:
            self.tabla_clases_activas.setRowCount(1)
            self.tabla_clases_activas.setItem(0, 0, QTableWidgetItem("Error al leer clases.json (archivo dañado)."))
            self.tabla_clases_activas.setSpan(0, 0, 1, 6)
            return
        except Exception as e:
            self.tabla_clases_activas.setRowCount(1)
            self.tabla_clases_activas.setItem(0, 0, QTableWidgetItem(f"Error inesperado al cargar clases: {e}"))
            self.tabla_clases_activas.setSpan(0, 0, 1, 6)
            return

        now = datetime.now()
        current_time = now.time()
        current_day = now.strftime("%A") # Nombre completo del día de la semana (e.g., "Monday")

        # Mapear nombres de días a español para comparación
        dias_semana_map = {
            "Monday": "Lunes",
            "Tuesday": "Martes",
            "Wednesday": "Miércoles",
            "Thursday": "Jueves",
            "Friday": "Viernes",
            "Saturday": "Sábado",
            "Sunday": "Domingo"
        }
        current_day_spanish = dias_semana_map.get(current_day, "")

        active_classes = []
        for clase in clases:
            dias = clase.get("dias", [])
            hora_inicio_str = clase.get("hora_inicio")
            hora_fin_str = clase.get("hora_fin")

            if current_day_spanish in dias:
                try:
                    hora_inicio = dt_time.fromisoformat(hora_inicio_str)
                    hora_fin = dt_time.fromisoformat(hora_fin_str)

                    # Ajustar si la hora de fin es al día siguiente (ej. 23:00 - 01:00)
                    if hora_fin < hora_inicio:
                        # Si la hora actual es después de la hora de inicio O antes de la hora de fin
                        # (considerando que la clase termina al día siguiente)
                        if current_time >= hora_inicio or current_time <= hora_fin:
                            active_classes.append(clase)
                    else:
                        # Clase en el mismo día
                        if hora_inicio <= current_time <= hora_fin:
                            active_classes.append(clase)
                except ValueError:
                    # Manejar errores de formato de hora si es necesario
                    print(f"Advertencia: Formato de hora inválido para la clase: {clase.get('materia')}")
                    continue
        
        if not active_classes:
            self.tabla_clases_activas.setRowCount(1)
            no_clases_item = QTableWidgetItem("No hay clases activas en este momento.")
            no_clases_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_clases_activas.setItem(0, 0, no_clases_item)
            self.tabla_clases_activas.setSpan(0, 0, 1, 6) # Unir celdas
        else:
            self.tabla_clases_activas.setRowCount(len(active_classes))
            for row, clase in enumerate(active_classes):
                self.tabla_clases_activas.setItem(row, 0, QTableWidgetItem(clase.get("materia", "")))
                self.tabla_clases_activas.setItem(row, 1, QTableWidgetItem(clase.get("grupo", "")))
                self.tabla_clases_activas.setItem(row, 2, QTableWidgetItem(clase.get("docente", "")))
                self.tabla_clases_activas.setItem(row, 3, QTableWidgetItem(clase.get("salon", "")))
                self.tabla_clases_activas.setItem(row, 4, QTableWidgetItem(clase.get("hora_inicio", "")))
                self.tabla_clases_activas.setItem(row, 5, QTableWidgetItem(clase.get("hora_fin", "")))
            self.tabla_clases_activas.resizeColumnsToContents()
            self.tabla_clases_activas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)


    # La función reservar_salon ya no es necesaria en VerSalones si es solo para visualización
    # y la lógica de reserva se maneja en GestionarClases.
    # Si aún se necesita una acción de "reservar" desde aquí, se debe definir su lógica.
    # Por ahora, la función mostrar_info_salon() reemplaza la lógica previa de reserva directa.

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VerSalones()
    ventana.show()
    sys.exit(app.exec())
