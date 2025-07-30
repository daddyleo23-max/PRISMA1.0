from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QListWidget, QMessageBox
)
from PyQt6.QtCore import Qt
import json
import os

class DarAcceso(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget { background-color: #23272f; border-radius: 18px; }
            QLabel#titulo { color: #00e1ff; font-size: 28px; font-weight: bold; margin-bottom: 18px; }
            QLabel { color: #A3BE8C; font-size: 20px; font-weight: bold; }
            QLineEdit, QComboBox {
                background: #2E3440; color: #00e1ff; font-size: 22px;
                border: 2px solid #00e1ff; border-radius: 10px; padding: 12px; margin-bottom: 18px;
            }
            QPushButton {
                background-color: #00e1ff; color: #1e2229; font-size: 22px;
                border-radius: 16px; font-weight: bold; padding: 14px 0; min-width: 220px;
            }
            QPushButton:hover { background-color: #00b3cc; }
            QListWidget {
                background: #2E3440; color: #00e1ff; font-size: 18px;
                border: 2px solid #00e1ff; border-radius: 10px;
            }
        """)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(40)

        # --- Izquierda: buscar y asignar rol ---
        left_layout = QVBoxLayout()
        left_layout.setSpacing(18)
        main_layout.addLayout(left_layout, stretch=2)

        lbl_titulo = QLabel("Asignar acceso y rol")
        lbl_titulo.setObjectName("titulo")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(lbl_titulo)

        left_layout.addWidget(QLabel("Número de control (alumno) o placa (docente):"))
        self.input_id = QLineEdit()
        self.input_id.setPlaceholderText("Ejemplo: 21200903 o ISC4501879")
        self.input_id.returnPressed.connect(self.buscar_persona)
        left_layout.addWidget(self.input_id)

        self.lbl_nombre = QLabel("Nombre: ")
        self.lbl_tipo = QLabel("Tipo: ")
        self.lbl_area = QLabel("Área/Carrera: ")
        left_layout.addWidget(self.lbl_nombre)
        left_layout.addWidget(self.lbl_tipo)
        left_layout.addWidget(self.lbl_area)

        left_layout.addWidget(QLabel("Rol a asignar:"))
        self.selector_rol = QComboBox()
        self.selector_rol.addItems([
            "Maestro",   # Puede iniciar clases, abrir salones, áreas restringidas
            "Admin",     # Igual que maestro pero no es maestro
            "Super"      # Solo puede abrir/cerrar salones
        ])
        left_layout.addWidget(self.selector_rol)

        self.btn_asignar = QPushButton("Asignar rol")
        self.btn_asignar.clicked.connect(self.asignar_rol)
        self.btn_asignar.setEnabled(False)
        left_layout.addWidget(self.btn_asignar)

        left_layout.addStretch()

        # --- Derecha: lista de asignados ---
        right_layout = QVBoxLayout()
        right_layout.setSpacing(18)
        main_layout.addLayout(right_layout, stretch=1)

        lbl_lista = QLabel("Personas con rol asignado:")
        lbl_lista.setStyleSheet("color: #00e1ff; font-size: 20px; font-weight: bold;")
        right_layout.addWidget(lbl_lista)

        self.lista_roles = QListWidget()
        self.lista_roles.currentRowChanged.connect(self.seleccion_lista)
        right_layout.addWidget(self.lista_roles)

        # Botones modificar/eliminar
        self.btn_modificar = QPushButton("Modificar rol")
        self.btn_modificar.clicked.connect(self.modificar_rol)
        self.btn_modificar.setEnabled(False)
        right_layout.addWidget(self.btn_modificar)

        self.btn_eliminar = QPushButton("Eliminar acceso")
        self.btn_eliminar.clicked.connect(self.eliminar_rol)
        self.btn_eliminar.setEnabled(False)
        right_layout.addWidget(self.btn_eliminar)

        right_layout.addStretch()

        # Cargar personas y roles
        self.roles_json = self.cargar_roles()
        self.docentes = self.cargar_docentes()
        self.alumnos = self.cargar_alumnos()
        self.actualizar_lista_roles()

        self.persona_encontrada = None

    def cargar_docentes(self):
        if os.path.exists("docentes.json"):
            with open("docentes.json", "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except:
                    return []
        return []

    def cargar_alumnos(self):
        if os.path.exists("alumnos.json"):
            with open("alumnos.json", "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except:
                    return []
        return []

    def cargar_roles(self):
        if os.path.exists("roles.json"):
            with open("roles.json", "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except:
                    return []
        return []

    def buscar_persona(self):
        id_text = self.input_id.text().strip()
        self.persona_encontrada = None
        persona = next((d for d in self.docentes if d.get("placa", "").upper() == id_text.upper()), None)
        tipo = "Docente"
        area = ""
        if not persona:
            persona = next((a for a in self.alumnos if a.get("numero_control", "") == id_text), None)
            tipo = "Alumno"
        if persona:
            self.persona_encontrada = persona
            self.lbl_nombre.setText(f"Nombre: {persona.get('nombre','')}")
            self.lbl_tipo.setText(f"Tipo: {tipo}")
            area = persona.get("area") if tipo == "Docente" else persona.get("carrera")
            self.lbl_area.setText(f"Área/Carrera: {area if area else '-'}")
            self.btn_asignar.setEnabled(True)
        else:
            self.lbl_nombre.setText("Nombre: ")
            self.lbl_tipo.setText("Tipo: ")
            self.lbl_area.setText("Área/Carrera: ")
            self.btn_asignar.setEnabled(False)
            QMessageBox.warning(self, "No encontrado", "No se encontró la persona con ese número de control o placa.")

    def asignar_rol(self):
        if not self.persona_encontrada:
            QMessageBox.warning(self, "Error", "Busca primero la persona.")
            return
        tipo = self.lbl_tipo.text().replace("Tipo: ", "")
        id_persona = self.persona_encontrada.get("placa") if tipo == "Docente" else self.persona_encontrada.get("numero_control")
        rol = self.selector_rol.currentText()
        existente = next((r for r in self.roles_json if r["id"] == id_persona), None)
        if existente:
            existente["rol"] = rol
            existente["nombre"] = self.persona_encontrada["nombre"]
            existente["tipo"] = tipo
        else:
            self.roles_json.append({
                "id": id_persona,
                "nombre": self.persona_encontrada["nombre"],
                "tipo": tipo,
                "rol": rol
            })
        with open("roles.json", "w", encoding="utf-8") as f:
            json.dump(self.roles_json, f, ensure_ascii=False, indent=2)
        self.actualizar_lista_roles()
        QMessageBox.information(self, "Éxito", f"Rol asignado correctamente a {self.persona_encontrada['nombre']}.")

    def actualizar_lista_roles(self):
        self.lista_roles.clear()
        for r in self.roles_json:
            self.lista_roles.addItem(f"{r['nombre']} ({r['id']}) - {r['rol']}")
        self.btn_modificar.setEnabled(False)
        self.btn_eliminar.setEnabled(False)

    def seleccion_lista(self, idx):
        if idx >= 0 and idx < len(self.roles_json):
            self.btn_modificar.setEnabled(True)
            self.btn_eliminar.setEnabled(True)
            # Mostrar datos en los campos de la izquierda
            persona = self.roles_json[idx]
            self.lbl_nombre.setText(f"Nombre: {persona.get('nombre','')}")
            self.lbl_tipo.setText(f"Tipo: {persona.get('tipo','')}")
            # Buscar área/carrera según tipo
            area = "-"
            if persona["tipo"] == "Docente":
                doc = next((d for d in self.docentes if d.get("placa") == persona["id"]), None)
                area = doc.get("area") if doc else "-"
            else:
                alu = next((a for a in self.alumnos if a.get("numero_control") == persona["id"]), None)
                area = alu.get("carrera") if alu else "-"
            self.lbl_area.setText(f"Área/Carrera: {area}")
            # Selecciona el rol actual en el combo
            self.selector_rol.setCurrentText(persona.get("rol", "Maestro"))
            self.input_id.setText(persona["id"])
            self.btn_asignar.setEnabled(True)
            # Guarda la persona encontrada para modificar si se desea
            self.persona_encontrada = doc if persona["tipo"] == "Docente" else alu
        else:
            self.btn_modificar.setEnabled(False)
            self.btn_eliminar.setEnabled(False)
            self.lbl_nombre.setText("Nombre: ")
            self.lbl_tipo.setText("Tipo: ")
            self.lbl_area.setText("Área/Carrera: ")
            self.selector_rol.setCurrentIndex(0)
            self.input_id.clear()
            self.btn_asignar.setEnabled(False)
            self.persona_encontrada = None

    def modificar_rol(self):
        idx = self.lista_roles.currentRow()
        if idx < 0 or idx >= len(self.roles_json):
            return
        rol_actual = self.roles_json[idx]["rol"]
        nombre = self.roles_json[idx]["nombre"]
        id_persona = self.roles_json[idx]["id"]
        tipo = self.roles_json[idx]["tipo"]
        nuevo_rol, ok = QComboBox.getItem(self, "Modificar rol", "Selecciona nuevo rol:", ["Maestro", "Admin", "Super"], 0, False)
        if ok and nuevo_rol:
            self.roles_json[idx]["rol"] = nuevo_rol
            with open("roles.json", "w", encoding="utf-8") as f:
                json.dump(self.roles_json, f, ensure_ascii=False, indent=2)
            self.actualizar_lista_roles()
            QMessageBox.information(self, "Modificado", f"Rol modificado para {nombre} ({id_persona}).")

    def eliminar_rol(self):
        idx = self.lista_roles.currentRow()
        if idx < 0 or idx >= len(self.roles_json):
            return
        nombre = self.roles_json[idx]["nombre"]
        id_persona = self.roles_json[idx]["id"]
        confirm = QMessageBox.question(self, "Eliminar acceso", f"¿Seguro que deseas eliminar el acceso de {nombre} ({id_persona})?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.roles_json.pop(idx)
            with open("roles.json", "w", encoding="utf-8") as f:
                json.dump(self.roles_json, f, ensure_ascii=False, indent=2)
            self.actualizar_lista_roles()
            QMessageBox.information(self, "Eliminado", f"Acceso eliminado para {nombre} ({id_persona}).")