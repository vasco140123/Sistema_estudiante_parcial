import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app import db
from app.modelos.matricula import Matricula
from app.modelos.matricula_detalle import MatriculaDetalle
from app.modelos.estudiante import Estudiante
from app.modelos.estado_matricula import EstadoMatricula


class MatriculaService:

    @staticmethod
    def generar_pdf_ficha(matricula_id):
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
        from reportlab.platypus.flowables import HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors

        matricula = db.session.get(Matricula, matricula_id)
        if not matricula:
            return None, "Matrícula no encontrada"

        estudiante = db.session.get(Estudiante, matricula.estudiante_id)
        detalles = MatriculaDetalle.query.filter_by(matricula_id=matricula_id).all()

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
        styles = getSampleStyleSheet()
        negro = colors.HexColor("#000000")
        gris_claro = colors.HexColor("#f3f4f6")
        gris_medio = colors.HexColor("#d1d5db")
        gris_texto = colors.HexColor("#4b5563")

        elementos = []

        elementos.append(Paragraph("FICHA DE MATRÍCULA", ParagraphStyle("Title", fontSize=18, leading=22, fontName="Helvetica-Bold", spaceAfter=4, alignment=1)))
        elementos.append(Paragraph(f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}", ParagraphStyle("Fecha", fontSize=8, leading=10, fontName="Helvetica", textColor=gris_texto, alignment=1, spaceAfter=16)))
        elementos.append(HRFlowable(width="100%", thickness=1, color=gris_medio))
        elementos.append(Spacer(1, 12))

        elementos.append(Paragraph("DATOS DEL ESTUDIANTE", ParagraphStyle("Section", fontSize=11, leading=14, fontName="Helvetica-Bold", spaceAfter=8, spaceBefore=4)))

        data_est = [
            ["N° de Matrícula:", str(matricula.id), "Estado:", matricula.estado.nombre if matricula.estado else "N/A"],
            ["Estudiante:", f"{estudiante.nombres} {estudiante.apellido_paterno} {estudiante.apellido_materno}", "Pagado:", "Sí" if matricula.pagado else "No"],
            ["Correo:", estudiante.correo_institucional or "—", "", ""],
            ["Periodo:", matricula.periodo_academico.nombre if matricula.periodo_academico else "—", "Semestre:", matricula.semestre.codigo if matricula.semestre else "—"],
        ]
        col_widths = [100, 180, 70, 130]
        t_est = Table(data_est, colWidths=col_widths)
        t_est.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("GRID", (0, 0), (-1, -1), 0.5, gris_medio),
            ("BACKGROUND", (0, 0), (0, -1), gris_claro),
            ("BACKGROUND", (2, 0), (2, -1), gris_claro),
        ]))
        elementos.append(t_est)
        elementos.append(Spacer(1, 16))

        elementos.append(Paragraph("CURSOS MATRICULADOS", ParagraphStyle("Section", fontSize=11, leading=14, fontName="Helvetica-Bold", spaceAfter=8, spaceBefore=4)))

        if detalles:
            header = [["#", "Curso", "Créd.", "Docente", "Horario"]]
            rows = []
            for i, det in enumerate(detalles, 1):
                sec = det.seccion_curso
                curso_nombre = sec.curso.nombre if sec and sec.curso else f"Sección #{det.seccion_curso_id}"
                creditos = str(sec.curso.creditos) if sec and sec.curso else "—"
                docente = "—"
                if sec and sec.docentes_asignados:
                    doc_asignado = sec.docentes_asignados[0]
                    if doc_asignado.docente:
                        docente = f"{doc_asignado.docente.nombres} {doc_asignado.docente.apellido_paterno}"
                horario = ""
                if sec and sec.horarios:
                    horario = "; ".join([
                        f"Día {h.dia} {h.hora_inicio[:5]}-{h.hora_fin[:5]}"
                        for h in sec.horarios
                    ])
                rows.append([str(i), curso_nombre, creditos, docente, horario or "—"])

            t_cursos = Table(header + rows, colWidths=[30, 200, 40, 130, 120])
            t_cursos.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("BACKGROUND", (0, 0), (-1, 0), negro),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("ALIGN", (2, 0), (2, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, gris_medio),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, gris_claro]),
            ]))
            elementos.append(t_cursos)
        else:
            elementos.append(Paragraph("(Sin cursos registrados)", styles["Normal"]))

        doc.build(elementos)
        buffer.seek(0)
        return buffer, None

    @staticmethod
    def _nombre_periodo_actual(fecha=None):
        fecha = fecha or datetime.now()
        semestre = "I" if fecha.month <= 6 else "II"
        return f"{fecha.year}-{semestre}"

    @staticmethod
    def periodo_actual():
        from app.modelos.periodo_academico import PeriodoAcademico

        fecha = datetime.now()
        nombre = MatriculaService._nombre_periodo_actual(fecha)
        periodo = PeriodoAcademico.query.filter_by(nombre=nombre).first()

        if periodo:
            return periodo

        if fecha.month <= 6:
            fecha_inicio = datetime(fecha.year, 1, 1)
            fecha_fin = datetime(fecha.year, 6, 30)
        else:
            fecha_inicio = datetime(fecha.year, 7, 1)
            fecha_fin = datetime(fecha.year, 12, 31)

        periodo = PeriodoAcademico(nombre=nombre, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
        db.session.add(periodo)
        db.session.commit()
        return periodo

    @staticmethod
    def _cursos_aprobados_y_desaprobados(estudiante_id):
        from app.modelos.estado_curso import EstadoCurso

        matriculas_ids = [m.id for m in Matricula.query.filter_by(estudiante_id=estudiante_id, estado_id=3).all()]
        detalles = MatriculaDetalle.query.filter(MatriculaDetalle.matricula_id.in_(matriculas_ids)).all()

        aprobados = set()
        desaprobados = set()

        for d in detalles:
            estado = db.session.get(EstadoCurso, d.estado_curso_id)
            curso_id = d.seccion_curso.curso_id
            if estado and estado.nombre.lower() == "aprobado":
                aprobados.add(curso_id)
                desaprobados.discard(curso_id)
            elif estado and estado.nombre.lower() == "desaprobado":
                if curso_id not in aprobados:
                    desaprobados.add(curso_id)

        return aprobados, desaprobados

    @staticmethod
    def _cursos_matriculados_activos(estudiante_id):
        from app.modelos.estado_curso import EstadoCurso

        matriculas_ids = [m.id for m in Matricula.query.filter_by(estudiante_id=estudiante_id, estado_id=3).all()]
        detalles = MatriculaDetalle.query.filter(MatriculaDetalle.matricula_id.in_(matriculas_ids)).all()

        activos = set()
        for d in detalles:
            estado = db.session.get(EstadoCurso, d.estado_curso_id)
            if estado and estado.nombre.lower() == "cursando":
                activos.add(d.seccion_curso.curso_id)

        return activos

    @staticmethod
    def _prerequisitos_faltantes(curso_id, aprobados):
        from app.modelos.pre_requisito import PreRequisito

        requisitos = PreRequisito.query.filter_by(curso_dependiente_id=curso_id).all()
        return [r.curso_requisito for r in requisitos if r.curso_requisito_id not in aprobados]

    @staticmethod
    def cursos_disponibles(usuario_id, periodo_academico_id):
        from app.modelos.plan_estudiante import PlanEstudiante
        from app.modelos.plan_cursos_semestre import PlanCursosSemestre
        from app.modelos.seccion_curso import SeccionCurso

        estudiante = Estudiante.query.filter_by(usuario_id=usuario_id).first()
        if not estudiante:
            return None, "No se encontró un estudiante asociado a este usuario"

        plan_estudiante = PlanEstudiante.query.filter_by(estudiante_id=estudiante.id).first()
        if not plan_estudiante:
            return None, "El estudiante no tiene un plan de estudios asignado"

        plan_id = plan_estudiante.plan_estudios_id
        cursos_del_plan = PlanCursosSemestre.query.filter_by(plan_estudios_id=plan_id).order_by(
            PlanCursosSemestre.semestre_id
        ).all()

        aprobados, desaprobados = MatriculaService._cursos_aprobados_y_desaprobados(estudiante.id)
        matriculados_activos = MatriculaService._cursos_matriculados_activos(estudiante.id)

        semestres_ordenados = sorted(set(item.semestre_id for item in cursos_del_plan))
        intentados = aprobados | desaprobados

        if plan_estudiante.semestre_id:
            semestre_actual = plan_estudiante.semestre_id
            cursos_sem_actual = [i.curso_id for i in cursos_del_plan if i.semestre_id == semestre_actual]
            if cursos_sem_actual and all(c in intentados for c in cursos_sem_actual):
                idx = semestres_ordenados.index(semestre_actual) + 1 if semestre_actual in semestres_ordenados else len(semestres_ordenados)
                semestre_actual = semestres_ordenados[idx] if idx < len(semestres_ordenados) else semestres_ordenados[-1] + 1
        else:
            semestre_actual = semestres_ordenados[-1] if semestres_ordenados else 1
            for sem in semestres_ordenados:
                cursos_sem = [i.curso_id for i in cursos_del_plan if i.semestre_id == sem]
                if not all(c in intentados for c in cursos_sem):
                    semestre_actual = sem
                    break
            else:
                semestre_actual = semestres_ordenados[-1] + 1 if semestres_ordenados else 1

        creditos_maximos = 22
        resultado = []

        def agregar_curso(item, tipo):
            curso = item.curso
            ya_matriculado = curso.id in matriculados_activos
            faltantes = [] if ya_matriculado else MatriculaService._prerequisitos_faltantes(curso.id, aprobados)
            seccion = SeccionCurso.query.filter_by(
                periodo_academico_id=periodo_academico_id,
                curso_id=curso.id,
                semestre_id=item.semestre_id
            ).first()

            habilitado = len(faltantes) == 0 and seccion is not None and not ya_matriculado
            motivo = None
            if ya_matriculado:
                motivo = "Ya te encuentras matriculado en este curso"
            elif faltantes:
                motivo = "Falta aprobar: " + ", ".join(f.nombre for f in faltantes)
            elif not seccion:
                motivo = "No hay seccion disponible para este curso en el periodo actual"

            horarios = []
            aulas = set()
            if seccion:
                for h in seccion.horarios:
                    horarios.append({"dia": h.dia, "hora_inicio": str(h.hora_inicio), "hora_fin": str(h.hora_fin)})
                    if h.aula:
                        aulas.add(h.aula)

            resultado.append({
                "id": seccion.id if seccion else curso.id,
                "curso_id": curso.id,
                "nombre": curso.nombre,
                "curso_nombre": curso.nombre,
                "creditos": curso.creditos,
                "semestre_id": item.semestre_id,
                "tipo": tipo,
                "habilitado": habilitado,
                "motivo_bloqueo": motivo,
                "seccion_curso_id": seccion.id if seccion else None,
                "horarios": horarios,
                "aula": "; ".join(sorted(aulas)) if aulas else None
            })

        for item in cursos_del_plan:
            if item.semestre_id == semestre_actual:
                agregar_curso(item, "regular")

        for item in cursos_del_plan:
            if item.semestre_id < semestre_actual and item.curso_id in desaprobados:
                agregar_curso(item, "repetir")

        semestre_siguiente = semestre_actual + 1
        for item in cursos_del_plan:
            if item.semestre_id == semestre_siguiente:
                agregar_curso(item, "adelanto")

        regular = [c for c in resultado if c["tipo"] == "regular"]
        repetir = [c for c in resultado if c["tipo"] == "repetir"]
        adelanto = [c for c in resultado if c["tipo"] == "adelanto"]

        return {
            "semestre_actual": semestre_actual,
            "creditos_maximos_por_ciclo": creditos_maximos,
            "regular": regular,
            "repetir": repetir,
            "adelanto": adelanto,
        }, None

    @staticmethod
    def solicitar_matricula(usuario_id, secciones_seleccionadas, comprobante_path=None):
        from app.modelos.estado_curso import EstadoCurso

        if not secciones_seleccionadas:
            return None, "Debes seleccionar al menos un curso"

        periodo = MatriculaService.periodo_actual()
        disponibles, error = MatriculaService.cursos_disponibles(usuario_id, periodo.id)
        if error:
            return None, error

        estudiante_actual = Estudiante.query.filter_by(usuario_id=usuario_id).first()
        estados_activos = ["pendiente", "validado", "matriculado"]
        matricula_activa = (
            Matricula.query.filter_by(estudiante_id=estudiante_actual.id, periodo_academico_id=periodo.id)
            .join(EstadoMatricula, Matricula.estado_id == EstadoMatricula.id)
            .filter(db.func.lower(EstadoMatricula.nombre).in_(estados_activos))
            .first()
        )
        if matricula_activa:
            return None, "Ya tienes una solicitud de matricula activa para este periodo, no puedes enviar otra"

        todos_cursos = disponibles.get("regular", []) + disponibles.get("repetir", []) + disponibles.get("adelanto", [])
        mapa_disponibles = {c["seccion_curso_id"]: c for c in todos_cursos if c["seccion_curso_id"]}

        total_creditos = 0
        horarios_ocupados = []

        for seccion_id in secciones_seleccionadas:
            curso_info = mapa_disponibles.get(seccion_id)

            if not curso_info:
                return None, f"La seccion {seccion_id} no esta disponible para este estudiante"

            if not curso_info["habilitado"]:
                return None, f"No puedes llevar '{curso_info['curso_nombre']}': {curso_info['motivo_bloqueo']}"

            for h in curso_info["horarios"]:
                for ocupado in horarios_ocupados:
                    if h["dia"] == ocupado["dia"] and h["hora_inicio"] < ocupado["hora_fin"] and h["hora_fin"] > ocupado["hora_inicio"]:
                        return None, f"Cruce de horario con el curso '{curso_info['curso_nombre']}'"
                horarios_ocupados.append(h)

            total_creditos += curso_info["creditos"]

        if total_creditos > disponibles["creditos_maximos_por_ciclo"]:
            return None, f"Excedes el maximo de {disponibles['creditos_maximos_por_ciclo']} creditos por ciclo"

        estado_pendiente = EstadoMatricula.query.filter_by(nombre="Pendiente").first()
        estado_cursando = EstadoCurso.query.filter_by(nombre="Cursando").first()

        matricula = Matricula(
            estudiante_id=estudiante_actual.id,
            periodo_academico_id=periodo.id,
            semestre_id=disponibles["semestre_actual"],
            estado_id=estado_pendiente.id,
            comprobante_path=comprobante_path,
        )
        db.session.add(matricula)
        db.session.flush()

        for seccion_id in secciones_seleccionadas:
            detalle = MatriculaDetalle(
                matricula_id=matricula.id,
                seccion_curso_id=seccion_id,
                estado_curso_id=estado_cursando.id if estado_cursando else None,
            )
            db.session.add(detalle)

        db.session.commit()
        return {"id": matricula.id, "total_creditos": total_creditos}, None
