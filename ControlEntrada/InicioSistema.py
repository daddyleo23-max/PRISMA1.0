import sys
import os
import time
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QGraphicsOpacityEffect, QVBoxLayout
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QTimer, QThread, pyqtSignal, QRect, QParallelAnimationGroup
)
from PyQt6.QtGui import QPixmap, QColor

class PrismaticBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(900, 500)
        self.setStyleSheet("background-color: #1e2229;")

class SplashThread(QThread):
    loading_complete = pyqtSignal()
    def run(self):
        time.sleep(2)
        self.loading_complete.emit()

class SplashScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.container = PrismaticBackground()
        self.setCentralWidget(self.container)
        self.setFixedSize(900, 500)

        # Widget contenedor principal (fondo con bordes redondeados)
        self.main_container = QWidget(self)
        self.main_container.setGeometry(0, 0, 900, 500)
        self.main_container.setStyleSheet("""
            QWidget {
                background-color: #1e2229;
                border-radius: 20px;
            }
        """)

        # Contenedor central para el logo (con bordes redondeados, sin sombra)
        self.shadow_container = QWidget(self.main_container)
        self.shadow_container.setGeometry(100, 75, 700, 350)
        self.shadow_container.setStyleSheet("""
            background-color: transparent;
            border-radius: 20px;
        """)

        # Imagen dentro del contenedor
        self.image_label = QLabel(self.shadow_container)
        base_dir = os.path.dirname(__file__)
        image_path = os.path.join(base_dir, "..", "Images", "logoDSP.png")
        image_path = os.path.abspath(image_path)
        self.pixmap = QPixmap(image_path)
        if self.pixmap.isNull():
            self.pixmap = QPixmap(700, 350)
            self.pixmap.fill(QColor("#2d323b"))
        self.image_label.setPixmap(self.pixmap.scaled(
            700, 350,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
        self.image_label.setGeometry(0, 0, 700, 350)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Efecto de opacidad aplicado a la imagen
        self.opacity_effect = QGraphicsOpacityEffect(self.image_label)
        self.image_label.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)

        # Animación de opacidad (fade-in)
        self.opacity_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_anim.setDuration(6000)
        self.opacity_anim.setStartValue(0)
        self.opacity_anim.setEndValue(1)
        self.opacity_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Animación de escala (zoom in) sobre el logo
        self.scale_anim = QPropertyAnimation(self.image_label, b"geometry")
        self.scale_anim.setDuration(1600)
        start_rect = QRect(325, 140, 250, 120)
        end_rect = QRect(0, 0, 700, 350)
        self.scale_anim.setStartValue(start_rect)
        self.scale_anim.setEndValue(end_rect)
        self.scale_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Grupo de animaciones paralelas
        self.anim_group = QParallelAnimationGroup()
        self.anim_group.addAnimation(self.opacity_anim)
        self.anim_group.addAnimation(self.scale_anim)
        self.anim_group.finished.connect(self.animar_logo_fadeout)

        # Texto y puntos de progreso (inicialmente ocultos)
        self.text_label = QLabel("Dynamic System for Person", self.main_container)
        self.text_label.setStyleSheet("color: #00e1ff; font-size: 28px; font-weight: bold;")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setGeometry(0, 370, 900, 50)
        self.text_label.hide()

        self.dots_label = QLabel("", self.main_container)
        self.dots_label.setStyleSheet("color: #00e1ff; font-size: 32px;")
        self.dots_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dots_label.setGeometry(0, 410, 900, 50)
        self.dots_label.hide()

        # Inicia animaciones
        QTimer.singleShot(100, self.anim_group.start)

    def animar_logo_fadeout(self):
        # Animación de desvanecimiento del logo
        self.logo_fadeout = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.logo_fadeout.setDuration(3000)
        self.logo_fadeout.setStartValue(1)
        self.logo_fadeout.setEndValue(0)
        self.logo_fadeout.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.logo_fadeout.finished.connect(self.mostrar_texto_y_puntos)
        self.logo_fadeout.start()

    def mostrar_texto_y_puntos(self):
        self.image_label.hide() # Oculta el logo después del fadeout
        self.text_label.show()
        self.dots_label.show()
        self.punto_actual = 0
        self.max_puntos = 12 # 12 ciclos de puntos (~3s)
        self.animar_puntos()

    def animar_puntos(self):
        puntos = "." * ((self.punto_actual % 4) + 1)
        self.dots_label.setText(puntos)
        self.punto_actual += 1
        if self.punto_actual < self.max_puntos:
            QTimer.singleShot(250, self.animar_puntos)
        else:
            self.transition_to_bienvenida()

    def transition_to_bienvenida(self):
        from CentralBienvenida import CentralBienvenida
        docentes = [
            {"nombre": "Mtro. Juan Pérez"},
            {"nombre": "Dra. Ana López"},
            {"nombre": "Ing. Carlos Ruiz"},
            {"nombre": "Lic. María Torres"}
        ]
        self.central_bienvenida = CentralBienvenida(docentes)
        self.central_bienvenida.showFullScreen()  # <<--- Esto garantiza pantalla completa
       
        self.close()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()
    sys.exit(app.exec())
