from io import BytesIO
from datetime import datetime

from sqlalchemy import func

from flask import jsonify, request, send_file
from flask_jwt_extended import get_jwt_identity
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from app import db
from app.modelos.historial_merito import HistorialMerito
from app.modelos.progreso_estudiante import ProgresoEstudiante
from app.modelos.tipo_clasificacion_merito import TipoClasificacionMerito
from app.modelos.estado_permanencia_estudiante import EstadoPermanenciaEstudiante
from app.modelos.estudiante import Estudiante
from app.modelos.matricula import Matricula
from app.modelos.matricula_detalle import MatriculaDetalle
from app.modelos.plan_estudiante import PlanEstudiante
from app.modelos.plan_cursos_semestre import PlanCursosSemestre
from app.modelos.curso import Curso


def obtener_record(estudiante_id):
    historial = HistorialMerito.query.filter_by(estudiante_id=estudiante_id).all()
    return jsonify([
        {
            "periodo_academico_id": h.periodo_academico_id,
            "semestre_id": h.semestre_id,
            "promedio_ponderado_periodo": float(h.promedio_ponderado_periodo),
            "creditos_aprobados_periodo": h.creditos_aprobados_periodo,
            "orden_merito": h.orden_merito,
            "tipo_clasificacion_id": h.tipo_clasificacion_id
        }
        for h in historial
    ])


def mi_historial():
    usuario_id = int(get_jwt_identity())
    estudiante = Estudiante.query.filter_by(usuario_id=usuario_id).first()

    if not estudiante:
        return jsonify({"error": "No se encontró un estudiante asociado a este usuario"}), 404

    historial = HistorialMerito.query.filter_by(estudiante_id=estudiante.id).all()
    progreso = db.session.get(ProgresoEstudiante, estudiante.id)

    cursos = []
    matriculas = Matricula.query.filter_by(estudiante_id=estudiante.id, estado_id=3).all()
    for mat in matriculas:
        for det in mat.detalle:
            cursos.append({
                "periodo_academico_nombre": mat.periodo_academico.nombre if mat.periodo_academico else "—",
                "curso_nombre": det.seccion_curso.curso.nombre if det.seccion_curso.curso else "—",
                "nota_final": float(det.nota_final) if det.nota_final is not None else None,
                "estado_nombre": det.estado_curso.nombre if det.estado_curso else "—",
            })

    plan_progreso = None
    plan_est = PlanEstudiante.query.filter_by(estudiante_id=estudiante.id).first()
    if plan_est:
        total_creditos = db.session.query(func.sum(Curso.creditos)).join(
            PlanCursosSemestre, PlanCursosSemestre.curso_id == Curso.id
        ).filter(
            PlanCursosSemestre.plan_estudios_id == plan_est.plan_estudios_id
        ).scalar() or 0

        creditos_aprobados = progreso.creditos_aprobados_acumulados if progreso else 0
        plan_progreso = {
            "plan_estudios_id": plan_est.plan_estudios_id,
            "total_creditos_requeridos": total_creditos,
            "creditos_aprobados": creditos_aprobados,
            "porcentaje": round((creditos_aprobados / total_creditos) * 100, 1)
                if total_creditos > 0 else 0,
        }

    return jsonify({
        "historial": [
            {
                "periodo_academico_id": h.periodo_academico_id,
                "periodo_academico_nombre": h.periodo_academico.nombre if h.periodo_academico else "—",
                "semestre_id": h.semestre_id,
                "semestre_codigo": h.semestre.codigo if h.semestre else "—",
                "promedio_ponderado_periodo": float(h.promedio_ponderado_periodo),
                "creditos_aprobados_periodo": h.creditos_aprobados_periodo,
                "orden_merito": h.orden_merito,
                "tipo_clasificacion_id": h.tipo_clasificacion_id,
                "tipo_clasificacion_nombre": h.tipo_clasificacion.nombre if h.tipo_clasificacion else "—"
            }
            for h in historial
        ],
        "progreso_actual": {
            "creditos_aprobados_acumulados": progreso.creditos_aprobados_acumulados,
            "promedio_ponderado_acumulado": float(progreso.promedio_ponderado_acumulado),
            "estado_permanencia_id": progreso.estado_permanencia_id,
            "estado_permanencia_nombre": progreso.estado_permanencia.nombre if progreso.estado_permanencia else "—"
        } if progreso else None,
        "cursos": cursos,
        "plan_progreso": plan_progreso,
    })


def obtener_progreso(estudiante_id):
    progreso = db.session.get(ProgresoEstudiante, estudiante_id)
    if not progreso:
        return jsonify({"mensaje": "Progreso de estudiante no encontrado"}), 404
    return jsonify({
        "estudiante_id": progreso.estudiante_id,
        "estado_permanencia_id": progreso.estado_permanencia_id,
        "creditos_aprobados_acumulados": progreso.creditos_aprobados_acumulados,
        "promedio_ponderado_acumulado": float(progreso.promedio_ponderado_acumulado)
    })


def listar_tipos_clasificacion():
    tipos = TipoClasificacionMerito.query.all()
    return jsonify([
        {"id": t.id, "nombre": t.nombre, "porcentaje_limite": float(t.porcentaje_limite)}
        for t in tipos
    ])


def listar_estados_permanencia():
    estados = EstadoPermanenciaEstudiante.query.all()
    return jsonify([
        {"id": e.id, "nombre": e.nombre, "descripcion": e.descripcion}
        for e in estados
    ])


def reportes_consolidados():
    total_estudiantes = Estudiante.query.count()
    total_con_progreso = ProgresoEstudiante.query.count()

    progresos = ProgresoEstudiante.query.all()
    promedio_general = None
    if progresos:
        suma = sum(float(p.promedio_ponderado_acumulado) for p in progresos)
        promedio_general = round(suma / len(progresos), 2)

    return jsonify({
        "total_estudiantes": total_estudiantes,
        "estudiantes_con_registro_de_progreso": total_con_progreso,
        "promedio_general_institucional": promedio_general
    })


def reportes_consolidados_pdf():
    from io import BytesIO
    from flask_jwt_extended import verify_jwt_in_request, get_jwt
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.platypus.flowables import HRFlowable

    token = request.args.get("token")
    if token:
        request.environ["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    try:
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get("rol") not in ("administrador", "direccion"):
            return jsonify({"error": "No tienes permiso para esta acci\u00f3n"}), 403
    except Exception:
        return jsonify({"error": "Autenticaci\u00f3n requerida"}), 401

    data_json = reportes_consolidados()
    cohortes_json = desempeno_por_cohorte()
    resumen = data_json.get_json()
    cohortes = cohortes_json.get_json()

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
    negro = colors.HexColor("#000000")
    gris_claro = colors.HexColor("#f3f4f6")
    gris_medio = colors.HexColor("#d1d5db")

    elementos = []
    elementos.append(Paragraph("REPORTE CONSOLIDADO", ParagraphStyle("Title", fontSize=18, leading=22, fontName="Helvetica-Bold", spaceAfter=4, alignment=1)))
    elementos.append(Paragraph(f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}", ParagraphStyle("Fecha", fontSize=8, leading=10, fontName="Helvetica", textColor=colors.HexColor("#4b5563"), alignment=1, spaceAfter=16)))
    elementos.append(HRFlowable(width="100%", thickness=1, color=negro))
    elementos.append(Spacer(1, 12))

    elementos.append(Paragraph("RESUMEN INSTITUCIONAL", ParagraphStyle("Section", fontSize=12, leading=15, fontName="Helvetica-Bold", spaceAfter=10, spaceBefore=4)))

    summary_data = [
        ["Total estudiantes", str(resumen.get("total_estudiantes", 0))],
        ["Con registro de progreso", str(resumen.get("estudiantes_con_registro_de_progreso", 0))],
        ["Promedio general institucional", str(resumen.get("promedio_general_institucional", "—"))],
    ]
    t = Table(summary_data, colWidths=[250, 200])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (0, -1), gris_claro),
        ("GRID", (0, 0), (-1, -1), 0.5, gris_medio),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
    ]))
    elementos.append(t)
    elementos.append(Spacer(1, 20))

    elementos.append(Paragraph("DESEMPEÑO POR COHORTE", ParagraphStyle("Section", fontSize=12, leading=15, fontName="Helvetica-Bold", spaceAfter=10, spaceBefore=4)))

    if cohortes:
        header = [["Especialidad", "Total estudiantes", "Promedio ponderado"]]
        rows = [[
            c.get("especialidad_nombre", f"ID {c.get('especialidad_id', '?')}"),
            str(c.get("total_estudiantes", 0)),
            str(c.get("promedio_ponderado", "—")),
        ] for c in cohortes]
        t2 = Table(header + rows, colWidths=[250, 100, 100])
        t2.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("BACKGROUND", (0, 0), (-1, 0), negro),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, gris_medio),
            ("ALIGN", (1, 0), (2, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, gris_claro]),
        ]))
        elementos.append(t2)
    else:
        elementos.append(Paragraph("No hay datos de cohorte disponibles.", ParagraphStyle("Normal", fontSize=10)))

    doc.build(elementos)
    buf.seek(0)
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name="reporte_consolidado.pdf")


def desempeno_por_cohorte():
    historiales = HistorialMerito.query.all()
    agrupado = {}

    for h in historiales:
        clave = h.especialidad_id or 0
        if clave not in agrupado:
            agrupado[clave] = {
                "especialidad_id": h.especialidad_id,
                "especialidad_nombre": h.especialidad.nombre if h.especialidad else "Sin especialidad",
                "promedios": [],
                "total_estudiantes": 0
            }
        agrupado[clave]["promedios"].append(float(h.promedio_ponderado_periodo))
        agrupado[clave]["total_estudiantes"] += 1

    resultado = []
    for clave, datos in agrupado.items():
        promedio = round(sum(datos["promedios"]) / len(datos["promedios"]), 2)
        resultado.append({
            "especialidad_id": datos["especialidad_id"],
            "especialidad_nombre": datos["especialidad_nombre"],
            "total_estudiantes": datos["total_estudiantes"],
            "promedio_ponderado": promedio
        })

    return jsonify(resultado)


def buscar_estudiantes():
    q = request.args.get("q", "").strip()
    if not q or len(q) < 2:
        return jsonify([])

    estudiantes = Estudiante.query.filter(
        db.or_(
            Estudiante.nombres.ilike(f"%{q}%"),
            Estudiante.apellido_paterno.ilike(f"%{q}%"),
            Estudiante.apellido_materno.ilike(f"%{q}%"),
            Estudiante.correo_institucional.ilike(f"%{q}%"),
            Estudiante.id.cast(db.String).ilike(f"%{q}%"),
        )
    ).filter(Estudiante.deleted_at.is_(None)).limit(20).all()

    return jsonify([
        {
            "id": e.id,
            "nombres": e.nombres,
            "apellido_paterno": e.apellido_paterno,
            "apellido_materno": e.apellido_materno,
            "nombre_completo": f"{e.nombres} {e.apellido_paterno} {e.apellido_materno}",
            "correo_institucional": e.correo_institucional,
            "especialidad_nombre": e.especialidad.nombre if e.especialidad else "—",
        }
        for e in estudiantes
    ])


def kardex_estudiante(estudiante_id):
    estudiante = db.session.get(Estudiante, estudiante_id)
    if not estudiante:
        return jsonify({"error": "Estudiante no encontrado"}), 404

    cursos = []
    matriculas = Matricula.query.filter_by(estudiante_id=estudiante.id, estado_id=3).all()
    for mat in matriculas:
        for det in mat.detalle:
            cursos.append({
                "periodo_academico_nombre": mat.periodo_academico.nombre if mat.periodo_academico else "—",
                "curso_nombre": det.seccion_curso.curso.nombre if det.seccion_curso.curso else "—",
                "creditos": det.seccion_curso.curso.creditos if det.seccion_curso.curso else 0,
                "nota_final": float(det.nota_final) if det.nota_final is not None else None,
                "estado_nombre": det.estado_curso.nombre if det.estado_curso else "—",
            })

    progreso = db.session.get(ProgresoEstudiante, estudiante.id)

    historial = HistorialMerito.query.filter_by(estudiante_id=estudiante.id).all()

    plan_progreso = None
    plan_est = PlanEstudiante.query.filter_by(estudiante_id=estudiante.id).first()
    if plan_est:
        total_creditos = db.session.query(func.sum(Curso.creditos)).join(
            PlanCursosSemestre, PlanCursosSemestre.curso_id == Curso.id
        ).filter(
            PlanCursosSemestre.plan_estudios_id == plan_est.plan_estudios_id
        ).scalar() or 0
        creditos_aprobados = progreso.creditos_aprobados_acumulados if progreso else 0
        plan_progreso = {
            "total_creditos_requeridos": total_creditos,
            "creditos_aprobados": creditos_aprobados,
            "porcentaje": round((creditos_aprobados / total_creditos) * 100, 1) if total_creditos > 0 else 0,
        }

    return jsonify({
        "estudiante": {
            "id": estudiante.id,
            "nombres": estudiante.nombres,
            "apellido_paterno": estudiante.apellido_paterno,
            "apellido_materno": estudiante.apellido_materno,
            "nombre_completo": f"{estudiante.nombres} {estudiante.apellido_paterno} {estudiante.apellido_materno}",
            "correo_institucional": estudiante.correo_institucional,
            "especialidad_nombre": estudiante.especialidad.nombre if estudiante.especialidad else "—",
            "facultad_nombre": estudiante.especialidad.facultad.nombre if estudiante.especialidad and estudiante.especialidad.facultad else "—",
        },
        "cursos": cursos,
        "progreso_actual": {
            "creditos_aprobados_acumulados": progreso.creditos_aprobados_acumulados,
            "promedio_ponderado_acumulado": float(progreso.promedio_ponderado_acumulado),
            "estado_permanencia_nombre": progreso.estado_permanencia.nombre if progreso.estado_permanencia else "—",
        } if progreso else None,
        "historial": [
            {
                "periodo_academico_nombre": h.periodo_academico.nombre if h.periodo_academico else "—",
                "promedio_ponderado_periodo": float(h.promedio_ponderado_periodo),
                "creditos_aprobados_periodo": h.creditos_aprobados_periodo,
                "orden_merito": h.orden_merito,
                "tipo_clasificacion_nombre": h.tipo_clasificacion.nombre if h.tipo_clasificacion else "—",
            }
            for h in historial
        ],
        "plan_progreso": plan_progreso,
    })


def descargar_kardex_pdf(estudiante_id):
    from flask_jwt_extended import verify_jwt_in_request, get_jwt
    from app.modulos.certificados.services import CertificadoService

    token = request.args.get("token")
    if token:
        request.environ["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    try:
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get("rol") not in ("administrador", "direccion"):
            return jsonify({"error": "No tienes permiso para esta acci\u00f3n"}), 403
    except Exception:
        return jsonify({"error": "Autenticaci\u00f3n requerida"}), 401

    data = kardex_estudiante(estudiante_id)
    if isinstance(data, tuple):
        return data

    estudiante = data.get_json()["estudiante"]
    cursos = data.get_json()["cursos"]
    progreso = data.get_json()["progreso_actual"]
    historial = data.get_json()["historial"]
    plan_data = data.get_json()["plan_progreso"]

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    negro = colors.HexColor("#000000")
    gris_claro = colors.HexColor("#f3f4f6")
    gris_medio = colors.HexColor("#d1d5db")
    gris_texto = colors.HexColor("#4b5563")

    styles.add(ParagraphStyle("Title2", fontSize=16, leading=20, spaceAfter=12, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle("Subtitle", fontSize=10, leading=14, textColor=gris_texto, spaceAfter=6))
    styles.add(ParagraphStyle("Small", fontSize=8, leading=10, fontName="Helvetica"))

    elementos = []

    elementos.append(Paragraph("KARDEX ACADÉMICO", styles["Title2"]))
    elementos.append(Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Subtitle"]))
    elementos.append(HRFlowable(width="100%", thickness=1, color=negro))
    elementos.append(Spacer(1, 12))

    data_est = [
        ["Estudiante:", estudiante["nombre_completo"], "Especialidad:", estudiante["especialidad_nombre"]],
        ["Facultad:", estudiante["facultad_nombre"], "Correo:", estudiante["correo_institucional"]],
    ]
    t = Table(data_est, colWidths=[80, 200, 80, 200])
    t.setStyle(TableStyle([
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
    elementos.append(t)
    elementos.append(Spacer(1, 10))

    if progreso:
        data_prog = [
            ["Promedio:", str(progreso["promedio_ponderado_acumulado"]),
             "Créditos:", str(progreso["creditos_aprobados_acumulados"]),
             "Estado:", progreso["estado_permanencia_nombre"]],
        ]
        t = Table(data_prog, colWidths=[55, 70, 55, 50, 45, 120])
        t.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTNAME", (4, 0), (4, -1), "Helvetica-Bold"),
            ("BACKGROUND", (0, 0), (-1, -1), gris_claro),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (1, 0), (3, 0), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("GRID", (0, 0), (-1, -1), 0.5, gris_medio),
        ]))
        elementos.append(t)
        elementos.append(Spacer(1, 12))

    elementos.append(Paragraph("CURSOS CURSADOS", styles["Title2"]))
    elementos.append(Spacer(1, 6))

    if cursos:
        header = [["Periodo", "Curso", "Créd.", "Nota", "Estado"]]
        rows = [[
            c["periodo_academico_nombre"],
            c["curso_nombre"],
            str(c["creditos"]),
            str(c["nota_final"]) if c["nota_final"] is not None else "—",
            c["estado_nombre"],
        ] for c in cursos]
        t = Table(header + rows, colWidths=[70, 190, 35, 40, 80])
        t.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("BACKGROUND", (0, 0), (-1, 0), negro),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (2, 0), (3, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, gris_medio),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, gris_claro]),
        ]))
        elementos.append(t)
    else:
        elementos.append(Paragraph("Sin cursos registrados.", styles["Normal"]))

    elementos.append(Spacer(1, 16))

    if plan_data:
        elementos.append(HRFlowable(width="100%", thickness=0.5, color=gris_medio))
        elementos.append(Spacer(1, 8))
        elementos.append(Paragraph(
            f"<b>Avance del plan:</b> {plan_data['creditos_aprobados']} / {plan_data['total_creditos_requeridos']} créditos ({plan_data['porcentaje']}%)",
            styles["Normal"]
        ))

    doc.build(elementos)
    buf.seek(0)
    return send_file(buf, mimetype="application/pdf", as_attachment=True,
                     download_name=f"kardex_{estudiante['id']}.pdf")