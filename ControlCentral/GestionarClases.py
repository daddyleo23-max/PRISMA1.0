from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QFormLayout, QCheckBox, QTimeEdit, QMessageBox,
    QListWidget, QListWidgetItem, QFrame, QFileDialog, QDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QStackedLayout # Importar QStackedLayout
)
from PyQt6.QtCore import Qt, QTime
import json
import os
from pdf_reader import extraer_datos_pdf # Asegúrate de que pdf_reader.py esté accesible

class GestionarClases(QWidget):
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
                font-size: 19px;
                font-weight: bold;
                margin-bottom: 2px;
            }
            QLineEdit {
                background: #23272f;
                color: #00e1ff;
                font-size: 18px;
                border: 1.5px solid #00e1ff;
                border-radius: 8px;
                padding: 7px 10px;
                margin-bottom: 10px;
            }
            QCheckBox {
                color: #A3BE8C;
                font-size: 17px;
            }
            QTimeEdit {
                background: #23272f;
                color: #00e1ff;
                font-size: 18px;
                border: 1.5px solid #00e1ff;
                border-radius: 8px;
                padding: 6px 8px;
                margin-bottom: 10px;
            }
            QPushButton {
                background-color: #00e1ff;
                color: #1e2229;
                font-size: 17px;
                border-radius: 10px;
                font-weight: bold;
                padding: 7px 0;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #00b3cc;
            }
            QListWidget {
                background: #23272f;
                color: #A3BE8C;
                border: 1.5px solid #00e1ff;
                border-radius: 8px;
                font-size: 17px;
                min-height: 60px;
            }
            QFrame#linea {
                color: #00e1ff;
                background: #00e1ff;
                max-height: 2px;
                min-height: 2px;
                border-radius: 1px;
            }
        """)

        self.alumnos = []
        self.cargar_alumnos() # Carga los nombres de los alumnos para la lista de asignación

        # Layout principal que contendrá el QStackedLayout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 20, 40, 20)
        main_layout.setSpacing(10)

        lbl_titulo = QLabel("Gestionar Clases")
        lbl_titulo.setObjectName("titulo")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(lbl_titulo)

        linea = QFrame()
        linea.setObjectName("linea")
        linea.setFrameShape(QFrame.Shape.HLine)
        linea.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(linea)

        # QStackedLayout para las dos páginas
        self.stacked_layout = QStackedLayout()
        main_layout.addLayout(self.stacked_layout)

        # --- Página 1: Datos de la Clase ---
        self.page1 = QWidget()
        page1_layout = QVBoxLayout(self.page1)
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setFormAlignment(Qt.AlignmentFlag.AlignHCenter)
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(8)

        # Materia
        self.input_materia = QLineEdit()
        self.input_materia.setPlaceholderText("Nombre de la materia")
        form.addRow(QLabel("Materia:"), self.input_materia)

        # Grupo
        self.input_grupo = QLineEdit()
        self.input_grupo.setPlaceholderText("Nombre del grupo")
        form.addRow(QLabel("Grupo:"), self.input_grupo)

        # Docente (ahora QComboBox)
        self.input_docente = QComboBox()
        self.cargar_docentes_combo() # Carga los docentes disponibles
        form.addRow(QLabel("Docente:"), self.input_docente)

        # Salón
        self.input_salon = QLineEdit()
        self.input_salon.setPlaceholderText("Nombre del salón")
        form.addRow(QLabel("Salón:"), self.input_salon)

        # Ciclo Escolar (solo lectura)
        self.input_ciclo = QLineEdit()
        self.input_ciclo.setReadOnly(False)  # Ahora editable
        self.input_ciclo.setPlaceholderText("Ciclo escolar (ejemplo: ENE-JUN/2025)")
        form.addRow(QLabel("Ciclo Escolar:"), self.input_ciclo)

        # Días de la semana
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        self.checkboxes_dias = []
        dias_layout = QHBoxLayout()
        for dia in dias:
            cb = QCheckBox(dia)
            dias_layout.addWidget(cb)
            self.checkboxes_dias.append(cb)
        form.addRow(QLabel("Días:"), dias_layout)

        # Hora de inicio y fin
        horas_layout = QHBoxLayout()
        self.time_inicio = QTimeEdit()
        self.time_inicio.setTime(QTime(8, 0))
        self.time_fin = QTimeEdit()
        self.time_fin.setTime(QTime(10, 0))
        horas_layout.addWidget(QLabel("Inicio:"))
        horas_layout.addWidget(self.time_inicio)
        horas_layout.addWidget(QLabel("Fin:"))
        horas_layout.addWidget(self.time_fin)
        form.addRow(QLabel("Horario:"), horas_layout)

        page1_layout.addLayout(form)

        # Botón Extraer PDF (en la primera página)
        btn_extraer = QPushButton("Extraer desde PDF")
        btn_extraer.clicked.connect(self.extraer_pdf)
        page1_layout.addWidget(btn_extraer, alignment=Qt.AlignmentFlag.AlignCenter)

        # Botón Continuar (para ir a la página de asignación de alumnos)
        btn_continuar = QPushButton("Continuar")
        btn_continuar.clicked.connect(self.validar_y_continuar)
        page1_layout.addWidget(btn_continuar, alignment=Qt.AlignmentFlag.AlignCenter)

        self.stacked_layout.addWidget(self.page1) # Añadir la página 1 al stacked layout

        # --- Página 2: Asignar Alumnos ---
        self.page2 = QWidget()
        page2_layout = QVBoxLayout(self.page2)
        
        lbl_alumnos = QLabel("Asignar Alumnos a la Clase:")
        lbl_alumnos.setStyleSheet("color: #00e1ff; font-size: 22px; font-weight: bold; margin-bottom: 10px;")
        page2_layout.addWidget(lbl_alumnos)

        self.input_buscar_alumno = QLineEdit()
        self.input_buscar_alumno.setPlaceholderText("Buscar alumno por nombre o número de control...")
        self.input_buscar_alumno.textChanged.connect(self.filtrar_alumnos)
        page2_layout.addWidget(self.input_buscar_alumno)

        self.lista_alumnos = QListWidget()
        self.lista_alumnos.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.lista_alumnos.setStyleSheet("""
            QListWidget {
                background: #2E3440; color: #ECEFF4; font-size: 18px;
                border: 2px solid #00e1ff; border-radius: 10px; padding: 10px;
            }
            QListWidget::item {
                padding: 8px;
            }
            QListWidget::item:selected {
                background-color: #00e1ff;
                color: #1e2229;
            }
        """)
        self.actualizar_lista_alumnos() # Carga los alumnos para la lista
        page2_layout.addWidget(self.lista_alumnos)

        # Botones de navegación para la página 2
        nav_buttons_layout = QHBoxLayout()
        btn_atras = QPushButton("Atrás")
        btn_atras.clicked.connect(self.mostrar_pagina1)
        nav_buttons_layout.addWidget(btn_atras)

        btn_guardar_clase = QPushButton("Guardar Clase")
        btn_guardar_clase.clicked.connect(self.guardar_clase)
        nav_buttons_layout.addWidget(btn_guardar_clase)
        
        page2_layout.addLayout(nav_buttons_layout)

        self.stacked_layout.addWidget(self.page2) # Añadir la página 2 al stacked layout

        self.stacked_layout.setCurrentIndex(0) # Iniciar en la primera página

    def validar_y_continuar(self):
        """Valida los campos de la primera página y avanza a la segunda."""
        materia = self.input_materia.text().strip()
        grupo = self.input_grupo.text().strip()
        docente = self.input_docente.currentText().strip()
        salon = self.input_salon.text().strip()
        ciclo = self.input_ciclo.text().strip()
        dias = [cb.text() for cb in self.checkboxes_dias if cb.isChecked()]
        hora_inicio = self.time_inicio.time().toString("HH:mm")
        hora_fin = self.time_fin.time().toString("HH:mm")

        if not materia or not grupo or not docente or not salon or not ciclo:
            QMessageBox.warning(self, "Error", "Todos los campos de la clase son obligatorios.")
            return
        if not dias:
            QMessageBox.warning(self, "Error", "Selecciona al menos un día para la clase.")
            return
        if hora_inicio >= hora_fin:
            QMessageBox.warning(self, "Error", "La hora de inicio debe ser antes que la de fin.")
            return
        
        # Guardar temporalmente los datos de la clase para usarlos en la página 2
        self.temp_clase_data = {
            "materia": materia,
            "grupo": grupo,
            "docente": docente,
            "salon": salon,
            "ciclo": ciclo,
            "dias": dias,
            "hora_inicio": hora_inicio,
            "hora_fin": hora_fin,
            "alumnos": [] # Se inicializa vacía, se llenará en la página 2
        }

        self.stacked_layout.setCurrentIndex(1) # Cambiar a la página de asignación de alumnos

    def mostrar_pagina1(self):
        """Vuelve a la primera página."""
        self.stacked_layout.setCurrentIndex(0)

    def cargar_alumnos(self):
        """Carga los datos completos de los alumnos desde alumnos.json."""
        try:
            if os.path.exists("alumnos.json"):
                with open("alumnos.json", "r", encoding="utf-8") as file:
                    self.alumnos = json.load(file)
            else:
                self.alumnos = []
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Error de Archivo", "El archivo alumnos.json está dañado o vacío. No se pudieron cargar los alumnos.")
            self.alumnos = []
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error inesperado al cargar alumnos: {e}")
            self.alumnos = []

    def actualizar_lista_alumnos(self, filtro=""):
        """Actualiza la lista de alumnos visibles en la UI según el filtro."""
        self.lista_alumnos.clear()
        for alumno in self.alumnos:
            nombre_completo = alumno.get("nombre", "")
            numero_control = alumno.get("numero_control", "")
            display_text = f"{nombre_completo} ({numero_control})"
            
            if filtro.lower() in nombre_completo.lower() or filtro.lower() in numero_control.lower():
                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, alumno) # Guarda el objeto alumno completo
                self.lista_alumnos.addItem(item)

    def filtrar_alumnos(self, texto):
        """Filtra la lista de alumnos al escribir en el campo de búsqueda."""
        self.actualizar_lista_alumnos(texto)

    def extraer_pdf(self):
        """Abre un diálogo para seleccionar un PDF y extrae datos de clase y alumnos."""
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
            # Asegurarse de que materia y grupo estén presentes
            if not datos.get("materia") or not datos.get("grupo"):
                QMessageBox.warning(self, "Error", "No se pudieron extraer materia o grupo del PDF. Verifica el formato.")
                return
            self.mostrar_confirmacion(datos)

    def mostrar_confirmacion(self, datos):
        """Muestra un diálogo de confirmación con los datos extraídos del PDF."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Confirmar importación")
        dialog.setMinimumSize(800, 500)
        layout = QVBoxLayout(dialog)

        materia = datos.get('materia', '')
        grupo = datos.get('grupo', '')
        profesor = datos.get('profesor', '')
        ciclo = datos.get('periodo', '')
        dias = datos.get('dias', [])
        horarios = datos.get('horarios', [])
        salones = datos.get('salones', [])
        alumnos_pdf = datos.get('alumnos', []) # Renombrado para evitar conflicto con self.alumnos

        layout.addWidget(QLabel(f"<b>Materia:</b> {materia}"))
        layout.addWidget(QLabel(f"<b>Grupo:</b> {grupo}"))
        layout.addWidget(QLabel(f"<b>Docente:</b> {profesor}"))
        layout.addWidget(QLabel(f"<b>Ciclo Escolar:</b> {ciclo}"))
        layout.addWidget(QLabel(f"<b>Días:</b> {', '.join(dias)}"))
        layout.addWidget(QLabel(f"<b>Horas:</b> {', '.join(horarios)}"))
        layout.addWidget(QLabel(f"<b>Salones:</b> {', '.join([s for s in salones if s])}"))
        layout.addWidget(QLabel(f"<b>Alumnos encontrados:</b> {len(alumnos_pdf)}"))

        tabla = QTableWidget()
        tabla.setColumnCount(2)
        tabla.setHorizontalHeaderLabels(["Nombre", "Número de Control"])
        tabla.setRowCount(len(alumnos_pdf))
        for i, alumno in enumerate(alumnos_pdf):
            tabla.setItem(i, 0, QTableWidgetItem(alumno.get("nombre", "")))
            tabla.setItem(i, 1, QTableWidgetItem(alumno.get("numero_control", "")))
        tabla.resizeColumnsToContents()
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(tabla)

        btn_confirmar = QPushButton("Usar estos datos")
        btn_confirmar.clicked.connect(lambda: self.rellenar_campos(datos, dialog))
        layout.addWidget(btn_confirmar)

        dialog.setLayout(layout)
        dialog.exec()

    def rellenar_campos(self, datos, dialog):
        """Rellena los campos del formulario con los datos extraídos del PDF y selecciona alumnos."""
        self.input_materia.setText(datos.get("materia", ""))
        self.input_grupo.setText(datos.get("grupo", ""))
        
        profesor = datos.get("profesor", "")
        idx = self.input_docente.findText(profesor)
        if idx >= 0:
            self.input_docente.setCurrentIndex(idx)
        else:
            self.input_docente.setCurrentIndex(-1)
            self.input_docente.setPlaceholderText(profesor if profesor else "Seleccionar Docente")

        self.input_ciclo.setText(datos.get("periodo", ""))

        dias = datos.get("dias", [])
        horarios = datos.get("horarios", [])
        salones = datos.get("salones", [])

        for cb in self.checkboxes_dias:
            cb.setChecked(False)

        for i, dia_nombre in enumerate(["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]):
            if dia_nombre in dias:
                cb = next((c for c in self.checkboxes_dias if c.text() == dia_nombre), None)
                if cb:
                    cb.setChecked(True)
                    try:
                        idx_dia_en_datos = dias.index(dia_nombre)
                        if idx_dia_en_datos < len(horarios) and horarios[idx_dia_en_datos].strip():
                            hora_ini, hora_fin = horarios[idx_dia_en_datos].split('-')
                            h_ini, m_ini = map(int, hora_ini.split(':'))
                            h_fin, m_fin = map(int, hora_fin.split(':'))
                            self.time_inicio.setTime(QTime(h_ini, m_ini))
                            self.time_fin.setTime(QTime(h_fin, m_fin))
                    except Exception:
                        pass

        salon = next((s for s in salones if s), "")
        self.input_salon.setText(salon)

        # Después de rellenar los campos de la clase, pasar a la página 2
        self.validar_y_continuar() # Esto también guardará los datos temporalmente
        
        # Ahora, en la página 2, selecciona los alumnos extraídos del PDF
        alumnos_pdf_numeros_control = [a["numero_control"] for a in datos.get("alumnos", [])]
        self.lista_alumnos.clearSelection() # Limpiar selecciones previas
        for i in range(self.lista_alumnos.count()):
            item = self.lista_alumnos.item(i)
            # Recupera el objeto alumno completo del UserRole
            alumno_data = item.data(Qt.ItemDataRole.UserRole)
            if alumno_data and alumno_data.get("numero_control") in alumnos_pdf_numeros_control:
                item.setSelected(True)
        dialog.accept()


    def guardar_clase(self):
        """Guarda la clase y sus alumnos asociados en clases.json y actualiza alumnos.json."""
        # Recuperar los datos de la clase guardados temporalmente
        if not hasattr(self, 'temp_clase_data'):
            QMessageBox.warning(self, "Error", "Primero completa los datos de la clase en el paso anterior.")
            return

        nueva_clase_data = self.temp_clase_data.copy()
        
        # Obtener los alumnos seleccionados de la lista
        alumnos_seleccionados_para_clase = []
        for item in self.lista_alumnos.selectedItems():
            alumno_data = item.data(Qt.ItemDataRole.UserRole)
            if alumno_data:
                alumnos_seleccionados_para_clase.append(alumno_data.get("numero_control"))
        
        # Aquí, la lista de alumnos en la clase en clases.json puede ser solo los números de control
        # o puedes decidir no guardarla aquí y que la relación sea solo en alumnos.json
        # Para este ejemplo, la dejaremos vacía en clases.json, ya que la relación es en alumnos.json
        nueva_clase_data["alumnos"] = [] # La relación se maneja en alumnos.json

        # Cargar clases existentes
        clases = []
        if os.path.exists("clases.json"):
            with open("clases.json", "r", encoding="utf-8") as file:
                try:
                    clases = json.load(file)
                except json.JSONDecodeError:
                    clases = []

        # Verificar si la clase ya existe para actualizar o añadir
        clase_existente = False
        for i, clase_guardada in enumerate(clases):
            if (clase_guardada.get("materia") == nueva_clase_data["materia"] and
                clase_guardada.get("grupo") == nueva_clase_data["grupo"] and
                clase_guardada.get("ciclo") == nueva_clase_data["ciclo"]):
                clases[i] = nueva_clase_data
                clase_existente = True
                break

        if not clase_existente:
            clases.append(nueva_clase_data)

        with open("clases.json", "w", encoding="utf-8") as file:
            json.dump(clases, file, indent=4, ensure_ascii=False)

        # --- Actualizar el campo 'clases' en alumnos.json para los alumnos seleccionados ---
        todos_los_alumnos = []
        if os.path.exists("alumnos.json"):
            with open("alumnos.json", "r", encoding="utf-8") as f:
                try:
                    todos_los_alumnos = json.load(f)
                except json.JSONDecodeError:
                    todos_los_alumnos = []

        # Nombre completo de la clase para añadir/eliminar en el campo 'clases' del alumno
        nombre_clase_para_alumno = (
            f"{nueva_clase_data['materia']} - {nueva_clase_data['grupo']} "
            f"({nueva_clase_data['docente']})"
        ).strip()

        for alumno in todos_los_alumnos:
            num_control_alumno = alumno.get("numero_control")
            if num_control_alumno in alumnos_seleccionados_para_clase:
                # Añadir la clase si no está ya
                if "clases" not in alumno:
                    alumno["clases"] = []
                if nombre_clase_para_alumno not in alumno["clases"]:
                    alumno["clases"].append(nombre_clase_para_alumno)
            else:
                # Si el alumno NO está seleccionado para esta clase, asegurarse de que no la tenga
                # Esto es importante si se edita una clase y se desasignan alumnos
                if "clases" in alumno and nombre_clase_para_alumno in alumno["clases"]:
                    alumno["clases"].remove(nombre_clase_para_alumno)

        with open("alumnos.json", "w", encoding="utf-8") as f:
            json.dump(todos_los_alumnos, f, ensure_ascii=False, indent=2)

        QMessageBox.information(self, "Éxito", "Clase y asignación de alumnos guardados correctamente.")
        
        # Limpiar campos y volver a la primera página
        self.input_materia.clear()
        self.input_grupo.clear()
        self.input_docente.setCurrentIndex(-1)
        self.input_salon.clear()
        self.input_ciclo.clear()
        for cb in self.checkboxes_dias:
            cb.setChecked(False)
        self.time_inicio.setTime(QTime(8, 0))
        self.time_fin.setTime(QTime(10, 0))
        self.lista_alumnos.clearSelection()
        self.stacked_layout.setCurrentIndex(0) # Volver a la primera página

    def cargar_docentes_combo(self):
        """Carga los nombres de los docentes desde docentes.json en el QComboBox."""
        self.input_docente.clear()
        try:
            if os.path.exists("docentes.json"):
                with open("docentes.json", "r", encoding="utf-8") as file:
                    docentes = json.load(file)
                    if isinstance(docentes, list):
                        for docente in docentes:
                            nombre = docente.get("nombre", "").strip()
                            if nombre:
                                self.input_docente.addItem(nombre)
            else:
                QMessageBox.warning(self, "Advertencia", "El archivo docentes.json no se encontró. No se pudieron cargar los docentes.")
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Error de Archivo", "El archivo docentes.json está dañado o vacío. No se pudieron cargar los docentes.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error inesperado al cargar docentes: {e}")

