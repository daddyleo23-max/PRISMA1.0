from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox

class ModoAdmin(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #23272f;")
        self.setWindowTitle("Modo Administrador")
        self.setMinimumSize(500, 400)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(24)

        self.lbl_titulo = QLabel("🔒 Acceso Administrador")
        self.lbl_titulo.setStyleSheet("font-size: 28px; color: #00e1ff; font-weight: bold;")
        self.layout.addWidget(self.lbl_titulo)

        self.lbl_instr = QLabel("Por favor, verifica tu huella para acceder a las opciones administrativas.")
        self.lbl_instr.setStyleSheet("font-size: 18px; color: #A3BE8C;")
        self.layout.addWidget(self.lbl_instr)

        self.btn_verificar = QPushButton("Simular verificación de huella")
        self.btn_verificar.setStyleSheet("""
            QPushButton {
                background-color: #3B4252;
                color: #A3BE8C;
                font-size: 18px;
                border-radius: 14px;
                padding: 10px 24px;
            }
            QPushButton:hover {
                background-color: #23272f;
                color: #00e1ff;
            }
        """)
        self.btn_verificar.clicked.connect(self.verificar_huella)
        self.layout.addWidget(self.btn_verificar)

        self.setLayout(self.layout)

    def verificar_huella(self):
        self.mostrar_opciones_admin()

    def mostrar_opciones_admin(self):
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        lbl = QLabel("Opciones administrativas disponibles:")
        lbl.setStyleSheet("font-size: 22px; color: #00e1ff; font-weight: bold;")
        self.layout.addWidget(lbl)

        #btn_registrar = QPushButton("Registrar alumnos/huellas")
        #btn_registrar.setStyleSheet("font-size: 18px;")
        #self.layout.addWidget(btn_registrar)

        btn_configurar = QPushButton("Configurar salones")
        btn_configurar.setStyleSheet("font-size: 18px;")
        self.layout.addWidget(btn_configurar)

        btn_salir = QPushButton("Salir del modo admin")
        btn_salir.setStyleSheet("font-size: 18px;")
        btn_salir.clicked.connect(self.close)
        self.layout.addWidget(btn_salir)