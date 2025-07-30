from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
import json
import os

class Historial(QWidget):
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
            QPushButton {
                background-color: #00e1ff;
                color: #1e2229;
                font-size: 18px;
                border-radius: 12px;
                font-weight: bold;
                padding: 10px 0;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #00b3cc;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(24)

        lbl_titulo = QLabel("⏳ Historial de Clases")
        lbl_titulo.setObjectName("titulo")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_titulo)

        # Tabla de historial
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels([
            "Fecha", "Clase", "Aula", "Duración", "Asistencia"
        ])
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.horizontalHeader().setMinimumSectionSize(120)
        layout.addWidget(self.tabla, stretch=1)

        # Botón para recargar historial
        btns = QHBoxLayout()
        btn_recargar = QPushButton("Recargar")
        btn_recargar.clicked.connect(self.cargar_historial)
        btns.addStretch()
        btns.addWidget(btn_recargar)
        layout.addLayout(btns)

        self.cargar_historial()

    def cargar_historial(self):
        self.tabla.setRowCount(0)
        historial = []
        if os.path.exists("historial.json"):
            with open("historial.json", "r", encoding="utf-8") as f:
                try:
                    historial = json.load(f)
                except json.JSONDecodeError:
                    QMessageBox.warning(self, "Error", "El archivo historial.json está dañado.")
                    return
        # Si tu historial está en otro archivo o estructura, cámbialo aquí

        for idx, clase in enumerate(historial):
            self.tabla.insertRow(idx)
            self.tabla.setItem(idx, 0, QTableWidgetItem(clase.get("fecha", "")))
            self.tabla.setItem(idx, 1, QTableWidgetItem(clase.get("materia", "")))
            self.tabla.setItem(idx, 2, QTableWidgetItem(clase.get("aula", "")))
            self.tabla.setItem(idx, 3, QTableWidgetItem(clase.get("duracion", "")))
            self.tabla.setItem(idx, 4, QTableWidgetItem(clase.get("asistencia", "")))