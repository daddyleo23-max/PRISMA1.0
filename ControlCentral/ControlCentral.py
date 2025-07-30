import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QApplication, QHBoxLayout, QFrame, QStackedLayout
)
from PyQt6.QtCore import Qt, QTimer, QTime, QPoint # Añadido QTime, QPoint para el reloj
from PyQt6.QtGui import QPainter, QPolygon, QColor, QPen, QFont # Añadido para el dibujo del reloj

# Importar todas las clases de los paneles que se van a usar
from GestionarClases import GestionarClases
from RegistrarAlumnos import RegistrarAlumnos
from ConsultarAlumnos import ConsultarAlumnos
from Historial import Historial
from ClasesRegistradas import ClasesRegistradas
from VerSalones import VerSalones
from RegistrarDocentes import RegistrarDocentes
from DarAcceso import DarAcceso

# --- Clase para el Panel de Bienvenida (integrada aquí) ---
class _WelcomePanel(QWidget):
    """
    Panel de bienvenida que muestra un reloj analógico y digital.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget {
                background-color: #2E3440; /* Fondo oscuro */
                color: #ECEFF4; /* Texto claro */
            }
            QLabel#welcomeTitle {
                color: #00e1ff; /* Azul brillante */
                font-size: 38px;
                font-weight: bold;
                margin-bottom: 20px;
            }
            QLabel#digitalClock {
                color: #A3BE8C; /* Verde suave */
                font-size: 48px;
                font-weight: bold;
                margin-top: 20px;
            }
            QFrame#analogClockFrame {
                border: 3px solid #00e1ff; /* Borde azul para el reloj */
                border-radius: 150px; /* Circular */
                background-color: #3B4252; /* Fondo del reloj */
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(30)

        # Título de bienvenida
        self.lbl_welcome_title = QLabel("¡Bienvenido al Sistema de Gestión!", self)
        self.lbl_welcome_title.setObjectName("welcomeTitle")
        self.lbl_welcome_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.lbl_welcome_title)

        # Reloj analógico (se dibuja en paintEvent)
        self.analog_clock_frame = QFrame(self)
        self.analog_clock_frame.setObjectName("analogClockFrame")
        self.analog_clock_frame.setFixedSize(300, 300) # Tamaño fijo para el reloj circular
        main_layout.addWidget(self.analog_clock_frame, alignment=Qt.AlignmentFlag.AlignCenter)

        # Reloj digital
        self.lbl_digital_clock = QLabel(self)
        self.lbl_digital_clock.setObjectName("digitalClock")
        self.lbl_digital_clock.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.lbl_digital_clock)

        # Timer para actualizar el reloj digital y el analógico
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clocks)
        # El timer no se inicia aquí, se iniciará/detendrá por ControlCentral

        self.update_clocks() # Llamar una vez para mostrar la hora inicial

    def start_timer(self):
        """Inicia el timer de actualización del reloj."""
        if not self.timer.isActive():
            self.timer.start(1000) # Actualizar cada segundo
            self.update_clocks() # Asegurar una actualización inmediata
            # print("DEBUG: _WelcomePanel timer started.")

    def stop_timer(self):
        """Detiene el timer de actualización del reloj."""
        if self.timer.isActive():
            self.timer.stop()
            # print("DEBUG: _WelcomePanel timer stopped.")

    def update_clocks(self):
        """Actualiza el reloj digital y fuerza el redibujado del analógico."""
        current_time = QTime.currentTime()
        self.lbl_digital_clock.setText(current_time.toString("hh:mm:ss AP")) # Formato 12 horas con AM/PM
        self.analog_clock_frame.update() # Fuerza el redibujado del QFrame para el reloj analógico

    def paintEvent(self, event):
        """Dibuja el reloj analógico en el QFrame."""
        painter = QPainter(self.analog_clock_frame)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Mover el origen al centro del frame del reloj
        side = min(self.analog_clock_frame.width(), self.analog_clock_frame.height())
        painter.translate(self.analog_clock_frame.width() / 2, self.analog_clock_frame.height() / 2)
        painter.scale(side / 200.0, side / 200.0) # Escalar para que se ajuste al tamaño del frame

        painter.setPen(Qt.PenStyle.NoPen)

        # Manecilla de la hora
        hour_hand = QPolygon([QPoint(7, 8), QPoint(-7, 8), QPoint(0, -40)])
        painter.setBrush(QColor("#ffffff")) # Blanco
        painter.save()
        time = QTime.currentTime()
        painter.rotate(30.0 * (time.hour() + time.minute() / 60.0))
        painter.drawConvexPolygon(hour_hand)
        painter.restore()

        # Manecilla de minutos
        minute_hand = QPolygon([QPoint(7, 8), QPoint(-7, 8), QPoint(0, -70)])
        painter.setBrush(QColor("#ffffff")) # Blanco
        painter.save()
        painter.rotate(6.0 * (time.minute() + time.second() / 60.0))
        painter.drawConvexPolygon(minute_hand)
        painter.restore()

        # Manecilla de segundos
        second_hand = QPolygon([QPoint(2, 8), QPoint(-2, 8), QPoint(0, -80)])
        painter.setBrush(QColor("#ff4d4d")) # Rojo
        painter.save()
        painter.rotate(6.0 * time.second())
        painter.drawConvexPolygon(second_hand)
        painter.restore()

        # Dibujar marcas del reloj
        painter.setPen(QPen(QColor("#00e1ff"), 2)) # Azul brillante
        for i in range(12):
            painter.drawLine(0, -88, 0, -96) # Marcas de hora
            painter.rotate(30.0)
        
        painter.setPen(QPen(QColor("#ffffff"), 1)) # Blanco
        for i in range(60):
            if i % 5 != 0: # No dibujar sobre las marcas de hora
                painter.drawLine(0, -92, 0, -96) # Marcas de minuto
            painter.rotate(6.0)

        # Dibujar el punto central
        painter.setBrush(QColor("#00e1ff"))
        painter.drawEllipse(-5, -5, 10, 10)


class ControlCentral(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dynamic System for Person")
        self.setGeometry(0, 0, 1200, 800)
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2E3440;
                color: #ECEFF4;
                font-size: 16px;
            }
        """)

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setCentralWidget(main_widget)

        # Panel izquierdo (botones)
        self.panel_izq = QWidget()
        self.panel_izq.setFixedWidth(370)
        self.panel_izq.setStyleSheet("background-color: #23272f;")
        self.panel_izq_layout = QVBoxLayout(self.panel_izq)
        self.panel_izq_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.panel_izq_layout.setContentsMargins(30, 40, 30, 40)
        self.panel_izq_layout.setSpacing(24)

        # Definir las funciones categorizadas
        self.categorized_functions = {
            "Registros": [
                ("👨‍🏫 Registrar Docentes", self.abrir_registrar_docentes),
                ("👥 Registrar Alumnos", self.abrir_registrar_alumnos),
            ],
            "Gestión de Clases": [
                ("📚 Gestionar Clases", self.abrir_gestionar_clases),
                ("👜 Clases Registradas", self.abrir_clases_registradas),
            ],
            "Consultas y Reportes": [
                ("🕒 Consultar Alumnos", self.abrir_consultar_alumnos),
                ("⏳ Historial", self.abrir_historial),
            ],
            "Administración de Salones": [
                ("🔑 Dar Acceso", self.abrir_dar_acceso),
                ("🏫 Ver Salones", self.abrir_ver_salones),
            ]
        }
        
        # Instanciar el _WelcomePanel ANTES de llamar a display_main_menu
        self._welcome_panel = _WelcomePanel(self)

        # Mostrar el menú principal al inicio
        self.display_main_menu()

        # Línea divisoria vertical
        self.linea = QFrame()
        self.linea.setFrameShape(QFrame.Shape.VLine)
        self.linea.setFrameShadow(QFrame.Shadow.Sunken)
        self.linea.setStyleSheet("color: #00e1ff; background: #00e1ff; max-width: 2px;")

        # Área central
        self.area_central = QWidget()
        self.area_central.setStyleSheet("background-color: #2E3440;")
        self.area_central_layout = QVBoxLayout(self.area_central)
        self.area_central_layout.setContentsMargins(0, 0, 0, 0)

        # Mostrar el _WelcomePanel por defecto después de inicializarlo
        self.mostrar_panel_central(self._welcome_panel)

        # Botón hamburguesa para ocultar/mostrar barra lateral
        self.btn_toggle = QPushButton("≡")
        self.btn_toggle.setFixedSize(42, 42)
        self.btn_toggle.setStyleSheet("""
            QPushButton {
                background-color: #00e1ff;
                color: #23272f;
                font-size: 32px;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                margin: 8px;
            }
            QPushButton:hover {
                background-color: #00b3cc;
            }
        """)
        self.btn_toggle.clicked.connect(self.toggle_panel_izq)

        # Layout para el botón hamburguesa, arriba a la izquierda
        btn_toggle_layout = QHBoxLayout()
        btn_toggle_layout.setContentsMargins(0, 0, 0, 0)
        btn_toggle_layout.addWidget(self.btn_toggle, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        btn_toggle_layout.addStretch()

        # Widget contenedor para el área central y el botón hamburguesa
        central_container = QWidget()
        central_container_layout = QVBoxLayout(central_container)
        central_container_layout.setContentsMargins(0, 0, 0, 0)
        central_container_layout.setSpacing(0)
        central_container_layout.addLayout(btn_toggle_layout)
        central_container_layout.addWidget(self.area_central)

        # Añadir widgets al layout principal
        main_layout.addWidget(self.panel_izq)
        main_layout.addWidget(self.linea)
        main_layout.addWidget(central_container)

        self.panel_izq_visible = True  # Estado de visibilidad

    def clear_left_panel_layout(self):
        """Limpia todos los widgets del layout del panel izquierdo."""
        while self.panel_izq_layout.count():
            item = self.panel_izq_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def display_main_menu(self):
        """Muestra los botones de las categorías principales en el panel izquierdo."""
        self.clear_left_panel_layout()
        
        lbl_titulo = QLabel("Consola de Control")
        lbl_titulo.setStyleSheet("font-size: 28px; font-weight: bold; color: #00e1ff; margin-bottom: 30px;")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.panel_izq_layout.addWidget(lbl_titulo)

        for category_name in self.categorized_functions.keys():
            btn = QPushButton(category_name)
            btn.setFixedHeight(60)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #00e1ff;
                    color: #1e2229;
                    font-size: 20px;
                    border-radius: 14px;
                    font-weight: bold;
                    margin-bottom: 8px;
                    transition: background 0.2s;
                }
                QPushButton:hover {
                    background-color: #00b3cc;
                }
            """)
            btn.clicked.connect(lambda checked, name=category_name: self.display_sub_menu(name))
            self.panel_izq_layout.addWidget(btn)
        
        self.panel_izq_layout.addStretch()
        # No llamar a mostrar_panel_central aquí, ya se hace al final del __init__ y en display_sub_menu

    def display_sub_menu(self, category_name):
        """Muestra los botones de las sub-funciones para una categoría dada."""
        self.clear_left_panel_layout()

        lbl_category_title = QLabel(category_name)
        lbl_category_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #00e1ff; margin-bottom: 20px;")
        lbl_category_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.panel_izq_layout.addWidget(lbl_category_title)

        for text, func in self.categorized_functions[category_name]:
            btn = QPushButton(text)
            btn.setFixedHeight(60)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #00e1ff;
                    color: #1e2229;
                    font-size: 20px;
                    border-radius: 14px;
                    font-weight: bold;
                    margin-bottom: 8px;
                    transition: background 0.2s;
                }
                QPushButton:hover {
                    background-color: #00b3cc;
                }
            """)
            btn.clicked.connect(func)
            self.panel_izq_layout.addWidget(btn)

        btn_back = QPushButton("← Volver al Menú Principal")
        btn_back.setFixedHeight(60)
        btn_back.setStyleSheet("""
            QPushButton {
                background-color: #4C566A;
                color: #ECEFF4;
                font-size: 18px;
                border-radius: 14px;
                font-weight: bold;
                margin-top: 20px;
                transition: background 0.2s;
            }
            QPushButton:hover {
                background-color: #5E6778;
            }
        """)
        btn_back.clicked.connect(self.display_main_menu)
        self.panel_izq_layout.addWidget(btn_back)

        self.panel_izq_layout.addStretch()

    def toggle_panel_izq(self):
        self.panel_izq_visible = not self.panel_izq_visible
        self.panel_izq.setVisible(self.panel_izq_visible)
        self.linea.setVisible(self.panel_izq_visible)

    def mostrar_panel_central(self, widget):
        # Detener el timer del panel actual si es el WelcomePanel
        current_widget = None
        if self.area_central_layout.count() > 0:
            current_item = self.area_central_layout.itemAt(0)
            if current_item and current_item.widget():
                current_widget = current_item.widget()

        if current_widget is self._welcome_panel and widget is not self._welcome_panel:
            self._welcome_panel.stop_timer()

        # Limpia el área central antes de añadir el nuevo widget
        for i in reversed(range(self.area_central_layout.count())):
            w = self.area_central_layout.itemAt(i).widget()
            if w:
                w.setParent(None)
        
        # Añade el nuevo widget al área central
        self.area_central_layout.addWidget(widget)

        # Iniciar el timer del nuevo panel si es el WelcomePanel
        if widget is self._welcome_panel:
            self._welcome_panel.start_timer()

    # Métodos para abrir los paneles específicos
    def abrir_gestionar_clases(self):
        panel = GestionarClases(self)
        self.mostrar_panel_central(panel)

    def abrir_registrar_alumnos(self):
        panel = RegistrarAlumnos(self)
        self.mostrar_panel_central(panel)

    def abrir_consultar_alumnos(self):
        panel = ConsultarAlumnos(self)
        self.mostrar_panel_central(panel)

    def abrir_historial(self):
        panel = Historial(self)
        self.mostrar_panel_central(panel)

    def abrir_clases_registradas(self):
        panel = ClasesRegistradas(self)
        self.mostrar_panel_central(panel)
        
    def abrir_registrar_docentes(self):
        panel = RegistrarDocentes(self)
        self.mostrar_panel_central(panel)

    def abrir_dar_acceso(self):
        panel = DarAcceso(self)
        self.mostrar_panel_central(panel)
        
    def abrir_ver_salones(self):
        try:
            panel = VerSalones(self)
            self.mostrar_panel_central(panel)
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Error al abrir Ver Salones:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = ControlCentral()
    ventana.showMaximized()
    sys.exit(app.exec())
