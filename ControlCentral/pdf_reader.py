import re
from PyPDF2 import PdfReader

def extraer_datos_pdf(ruta_pdf):
    reader = PdfReader(ruta_pdf)
    texto = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
    texto = texto.upper()
    lines = texto.splitlines()

    # Extraer ciclo escolar (periodo)
    periodo = ""
    for i, line in enumerate(lines):
        if "PERIODO ESCOLAR" in line:
            if i+1 < len(lines):
                periodo = lines[i+1].strip()
            break

    # Extraer materia, clave y grupo
    match_mcg = re.search(r'MATERIA\s+CLAVE\s+GRUPO\s*\n([^\n]+)', texto)
    if match_mcg:
        linea = match_mcg.group(1).strip()
        partes = re.split(r'\s+', linea)
        materia = " ".join(partes[:-2]).strip() if len(partes) > 2 else (partes[0] if partes else "")
        clave = partes[-2].strip() if len(partes) > 1 else ""
        grupo = partes[-1].strip() if len(partes) > 0 else ""
    else:
        materia = clave = grupo = ""

    # Extraer profesor
    match_prof = re.search(r'RFC\s+CATEDRATICO\s*\n([A-Z0-9]+)\s+([^\n]+)', texto)
    if match_prof:
        profesor = match_prof.group(2).strip()
    else:
        profesor = ""

    # Extraer días, horarios y salones SOLO donde hay información
    dias_semana = []
    horarios_por_dia = []
    salones_por_dia = []
    for i, line in enumerate(lines):
        if re.match(r'LUNES\s+MARTES\s+MIERCOLES\s+JUEVES\s+VIERNES', line):
            dias_cabecera = re.findall(r'\b[A-ZÑÁÉÍÓÚ]+', line)
            if i+1 < len(lines):
                horarios_line = lines[i+1]
                columnas = re.split(r'\s{2,}', horarios_line)
                # Asegura que haya tantas columnas como días
                while len(columnas) < len(dias_cabecera):
                    columnas.append("")
                for idx, dia in enumerate(dias_cabecera):
                    col = columnas[idx].strip() if idx < len(columnas) else ""
                    if col:  # Solo si hay información en la columna
                        dias_semana.append(dia)
                        if "/" in col:
                            horario, salon = [x.strip() for x in col.split("/", 1)]
                        else:
                            horario, salon = col, ""
                        horarios_por_dia.append(horario)
                        salones_por_dia.append(salon)
            break

    # Extraer alumnos
    alumnos = []
    for line in lines:
        m = re.match(r'\d+\s+([A-ZÑÁÉÍÓÚ ]+?)\s+(\d{8})\s*$', line)
        if m:
            nombre = m.group(1).strip()
            numero_control = m.group(2).strip()
            correo = f"l{numero_control}@pachuca.tecnm.mx"
            alumnos.append({
                'nombre': nombre,
                'numero_control': numero_control,
                'correo': correo
            })

    curso = {
        'materia': materia,
        'clave': clave,
        'grupo': grupo,
        'profesor': profesor,
        'dias': dias_semana,           # Solo los días con información
        'horarios': horarios_por_dia,  # Solo los horarios de esos días
        'salones': salones_por_dia,    # Solo los salones de esos días
        'periodo': periodo,
        'alumnos': alumnos
    }
    return curso