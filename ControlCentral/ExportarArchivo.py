from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem,
    QDialog, QListWidget, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt
import json
import os
from pdf_reader import extraer_datos_pdf

class ExportarArchivo(QWidget):
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
            QPushButton {
                background-color: #00e1ff;
                color: #1e2229;
                font-size: 22px;
                border-radius: 16px;
                font-weight: bold;
                padding: 14px 0;
                min-width: 220px;
            }
            QPushButton:hover {
                background-color: #00b3cc;
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
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(24)

        lbl_titulo = QLabel("📄 Exportar Archivo PDF")
        lbl_titulo.setObjectName("titulo")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_titulo)

        btn_seleccionar = QPushButton("Seleccionar archivo PDF")
        btn_seleccionar.clicked.connect(self.seleccionar_pdf)
        layout.addWidget(btn_seleccionar, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def seleccionar_pdf(self):
        try:
            file_dialog = QFileDialog(self)
            file_dialog.setNameFilter("Archivos PDF (*.pdf)")
            if file_dialog.exec():
                pdf_path = file_dialog.selectedFiles()[0]
                try:
                    datos = extraer_datos_pdf(pdf_path)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Ocurrió un error al leer el PDF:\n{e}")
                    return
                if not datos:
                    QMessageBox.warning(self, "Error", "No se extrajo ningún dato del PDF.")
                    return
                if not datos.get("materia") or not datos.get("grupo"):
                    QMessageBox.warning(self, "Error", "No se pudieron extraer materia o grupo del PDF. Verifica el formato.")
                    return
                self.mostrar_confirmacion(datos)
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            QMessageBox.critical(self, "Error inesperado", str(e))

    def mostrar_confirmacion(self, datos):
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Confirmar importación")
            dialog.setMinimumSize(1000, 600)
            layout = QVBoxLayout(dialog)

            materia = datos.get('materia', '')
            grupo = datos.get('grupo', '')
            profesor = datos.get('profesor', '')
            horario = datos.get('horario', '')
            alumnos = datos.get('alumnos', [])

            layout.addWidget(QLabel(f"<b>Materia:</b> {materia}"))
            layout.addWidget(QLabel(f"<b>Grupo:</b> {grupo}"))
            layout.addWidget(QLabel(f"<b>Profesor:</b> {profesor}"))
            layout.addWidget(QLabel(f"<b>Horario:</b> {horario}"))
            layout.addWidget(QLabel(f"<b>Alumnos encontrados:</b> {len(alumnos)}"))

            tabla = QTableWidget()
            tabla.setColumnCount(2)
            tabla.setHorizontalHeaderLabels(["Nombre", "Número de Control"])
            tabla.setRowCount(len(alumnos))
            for i, alumno in enumerate(alumnos):
                tabla.setItem(i, 0, QTableWidgetItem(alumno.get("nombre", "")))
                tabla.setItem(i, 1, QTableWidgetItem(alumno.get("numero_control", "")))
            tabla.resizeColumnsToContents()
            tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            layout.addWidget(tabla)

            btn_confirmar = QPushButton("Registrar en la base de datos")
            btn_confirmar.clicked.connect(lambda: self.registrar_datos(datos, dialog))
            layout.addWidget(btn_confirmar)

            dialog.setLayout(layout)
            dialog.exec()
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            QMessageBox.critical(self, "Error inesperado", str(e))

    def registrar_datos(self, datos, dialog):
        try:
            materia = datos.get('materia', '')
            grupo = datos.get('grupo', '')
            horario = datos.get('horario', '')
            profesor = datos.get('profesor', '')
            alumnos = datos.get('alumnos', [])

            # Guardar clase en clases.json
            clase_nueva = {
                "materia": materia,
                "grupo": grupo,
                "horario": horario,
                "profesor": profesor
            }
            try:
                with open("clases.json", "r", encoding="utf-8") as f:
                    clases = json.load(f)
            except Exception:
                clases = []
            if not any(c["materia"] == materia and c["grupo"] == grupo for c in clases):
                clases.append(clase_nueva)
                with open("clases.json", "w", encoding="utf-8") as f:
                    json.dump(clases, f, ensure_ascii=False, indent=2)

            # Guardar alumnos en alumnos.json
            try:
                with open("alumnos.json", "r", encoding="utf-8") as f:
                    alumnos_json = json.load(f)
            except Exception:
                alumnos_json = []
            clase_str = f"{materia} - {grupo}"
            for alumno in alumnos:
                numero_control = alumno.get("numero_control", "")
                existente = next((a for a in alumnos_json if a.get("numero_control") == numero_control), None)
                if existente:
                    if "clases" not in existente:
                        existente["clases"] = []
                    if clase_str not in existente["clases"]:
                        existente["clases"].append(clase_str)
                else:
                    alumnos_json.append({
                        "nombre": alumno.get("nombre", ""),
                        "carrera": "",
                        "numero_control": numero_control,
                        "correo": f"l{numero_control}@pachuca.tecnm.mx",
                        "clases": [clase_str]
                    })
            with open("alumnos.json", "w", encoding="utf-8") as f:
                json.dump(alumnos_json, f, ensure_ascii=False, indent=2)

            dialog.accept()
            self.mostrar_exito(materia, grupo, alumnos)
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            QMessageBox.critical(self, "Error inesperado", str(e))

    def mostrar_exito(self, materia, grupo, alumnos):
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Importación exitosa")
            dialog.setMinimumSize(1000, 600)
            layout = QVBoxLayout(dialog)
            layout.addWidget(QLabel(f"<b>¡Clase y grupo agregados correctamente!</b>"))
            layout.addWidget(QLabel(f"<b>Materia:</b> {materia}"))
            layout.addWidget(QLabel(f"<b>Grupo:</b> {grupo}"))
            layout.addWidget(QLabel(f"<b>Alumnos registrados:</b>"))

            lista_alumnos = QListWidget()
            for alumno in alumnos:
                lista_alumnos.addItem(f"{alumno['nombre']} ({alumno['numero_control']})")
            layout.addWidget(lista_alumnos)

            btn_cerrar = QPushButton("Cerrar")
            btn_cerrar.clicked.connect(dialog.accept)
            layout.addWidget(btn_cerrar)

            dialog.setLayout(layout)
            dialog.exec()
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            QMessageBox.critical(self, "Error inesperado", str(e))