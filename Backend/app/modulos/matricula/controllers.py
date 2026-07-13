import os
from datetime import datetime

from flask import jsonify, request, send_file
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app import db
from app.modelos.estudiante import Estudiante
from app.modelos.periodo_academico import PeriodoAcademico
from app.modelos.seccion_curso import SeccionCurso
from app.modelos.matricula import Matricula
from app.modelos.estado_matricula import EstadoMatricula
from app.modelos.auditoria import Auditoria
from app.modulos.matricula.services import MatriculaService


def listar_periodos():
    periodos = PeriodoAcademico.query.order_by(PeriodoAcademico.fecha_inicio.desc()).all()
    return jsonify([
        {
            "id": p.id,
            "nombre": p.nombre,
            "fecha_inicio": p.fecha_inicio,
            "fecha_fin": p.fecha_fin
        }
        for p in periodos
    ])


def periodo_actual():
    periodo = MatriculaService.periodo_actual()
    return jsonify({
        "id": periodo.id,
        "nombre": periodo.nombre,
        "fecha_inicio": periodo.fecha_inicio.isoformat() if isinstance(periodo.fecha_inicio, datetime) else periodo.fecha_inicio,
        "fecha_fin": periodo.fecha_fin.isoformat() if isinstance(periodo.fecha_fin, datetime) else periodo.fecha_fin
    })


def listar_secciones():
    periodo = MatriculaService.periodo_actual()
    secciones = SeccionCurso.query.filter_by(periodo_academico_id=periodo.id).all()

    return jsonify([
        {
            "id": s.id,
            "periodo_academico_nombre": s.periodo_academico.nombre,
            "periodo_academico_id": s.periodo_academico_id,
            "curso_nombre": s.curso.nombre,
            "curso_id": s.curso_id,
            "semestre_codigo": s.semestre.codigo,
            "semestre_id": s.semestre_id,
            "cupos": s.cupos
        }
        for s in secciones
    ])


def listar_matriculas():
    matriculas = Matricula.query.filter(Matricula.deleted_at.is_(None)).all()
    return jsonify([
        {
            "id": m.id,
            "estudiante_id": m.estudiante_id,
            "estudiante_nombre": f"{m.estudiante.nombres} {m.estudiante.apellido_paterno}" if m.estudiante else "—",
            "periodo_academico_id": m.periodo_academico_id,
            "periodo_academico_nombre": m.periodo_academico.nombre if m.periodo_academico else "—",
            "semestre_id": m.semestre_id,
            "semestre_codigo": m.semestre.codigo if m.semestre else "—",
            "estado_id": m.estado_id,
            "estado_nombre": m.estado.nombre if m.estado else "—",
            "pagado": m.pagado,
            "tiene_comprobante": m.comprobante_path is not None,
        }
        for m in matriculas
    ])


def crear_matricula():
    import os
    from werkzeug.utils import secure_filename

    usuario_id = int(get_jwt_identity())

    if request.is_json:
        data = request.get_json()
        secciones_seleccionadas = data.get("secciones_curso_ids", [])
        comprobante_path = None
    else:
        secciones_seleccionadas = request.form.get("secciones_curso_ids", type=lambda v: [int(x) for x in v.split(",") if x.strip().isdigit()]) or []
        archivo = request.files.get("comprobante")
        comprobante_path = None
        if archivo and archivo.filename:
            carpeta = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "comprobantes")
            os.makedirs(carpeta, exist_ok=True)
            nombre = f"{usuario_id}_{int(datetime.now().timestamp())}_{secure_filename(archivo.filename)}"
            ruta = os.path.join(carpeta, nombre)
            archivo.save(ruta)
            comprobante_path = ruta

    if not isinstance(secciones_seleccionadas, list) or not secciones_seleccionadas:
        return jsonify({"error": "Debes enviar una lista de IDs de secciones"}), 400

    if not all(isinstance(s, int) for s in secciones_seleccionadas):
        return jsonify({"error": "Todos los IDs de secciones deben ser numeros enteros"}), 400

    resultado, error = MatriculaService.solicitar_matricula(usuario_id, secciones_seleccionadas, comprobante_path)

    if error:
        return jsonify({"error": error}), 400

    return jsonify({"mensaje": "Solicitud de matrícula registrada", "matricula_id": resultado.get("id"), **resultado}), 201


def listar_estados_matricula():
    estados = EstadoMatricula.query.all()
    return jsonify([
        {"id": e.id, "nombre": e.nombre}
        for e in estados
    ])


def validar_requisitos(matricula_id):
    matricula = db.session.get(Matricula, matricula_id)
    if not matricula:
        return jsonify({"error": "Matrícula no encontrada"}), 404

    if matricula.estado_id != 1:
        return jsonify({"error": "Solo se pueden validar matrículas pendientes"}), 400

    matricula.estado_id = 2

    Auditoria.registrar(
        usuario_id=int(get_jwt_identity()),
        accion="validar_matricula",
        detalle=f"Matrícula #{matricula_id} validada (pendiente→validada)"
    )

    db.session.commit()

    return jsonify({"mensaje": "Requisitos validados", "matricula_id": matricula.id})


def registrar_pago(matricula_id):
    matricula = db.session.get(Matricula, matricula_id)
    if not matricula:
        return jsonify({"error": "Matrícula no encontrada"}), 404

    if matricula.estado_id != 2:
        return jsonify({"error": "La matrícula debe estar validada antes de registrar el pago"}), 400

    matricula.pagado = True

    Auditoria.registrar(
        usuario_id=int(get_jwt_identity()),
        accion="registrar_pago",
        detalle=f"Pago registrado para matrícula #{matricula_id}"
    )

    db.session.commit()

    return jsonify({"mensaje": "Pago registrado", "matricula_id": matricula.id})


def generar_ficha_oficial(matricula_id):
    matricula = db.session.get(Matricula, matricula_id)
    if not matricula:
        return jsonify({"error": "Matrícula no encontrada"}), 404

    if not matricula.pagado:
        return jsonify({"error": "No se puede generar la ficha sin el pago registrado"}), 400

    matricula.estado_id = 3

    Auditoria.registrar(
        usuario_id=int(get_jwt_identity()),
        accion="generar_ficha_matricula",
        detalle=f"Ficha oficial generada para matrícula #{matricula_id}"
    )

    db.session.commit()

    return jsonify({
        "mensaje": "Ficha oficial generada, matrícula confirmada",
        "matricula": {
            "id": matricula.id,
            "estudiante_id": matricula.estudiante_id,
            "estado_id": matricula.estado_id,
            "estado_nombre": matricula.estado.nombre if matricula.estado else "—",
            "pagado": matricula.pagado,
        }
    })


def estadisticas():
    query = Matricula.query.filter(Matricula.deleted_at.is_(None))
    total = query.count()
    matriculados = query.filter_by(estado_id=3).count()
    pendientes = query.filter_by(estado_id=1).count()
    validados = query.filter_by(estado_id=2).count()

    return jsonify({
        "total_solicitudes": total,
        "matriculados": matriculados,
        "pendientes": pendientes,
        "validados": validados
    })


def descargar_ficha(matricula_id):
    token = request.args.get("token")
    if token:
        request.environ["HTTP_AUTHORIZATION"] = f"Bearer {token}"

    try:
        verify_jwt_in_request()
    except Exception:
        return jsonify({"error": "Autenticación requerida. Usa ?token=... en el enlace"}), 401

    matricula = db.session.get(Matricula, matricula_id)
    if not matricula:
        return jsonify({"error": "Matrícula no encontrada"}), 404

    usuario_id = int(get_jwt_identity())
    estudiante = Estudiante.query.filter_by(usuario_id=usuario_id).first()
    if not estudiante or matricula.estudiante_id != estudiante.id:
        return jsonify({"error": "No tienes acceso a esta matrícula"}), 403

    buffer, error = MatriculaService.generar_pdf_ficha(matricula_id)

    if error:
        return jsonify({"error": error}), 404

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"ficha_matricula_{matricula_id}.pdf",
        mimetype="application/pdf"
    )


def mis_matriculas():
    usuario_id = int(get_jwt_identity())
    estudiante = Estudiante.query.filter_by(usuario_id=usuario_id).first()
    if not estudiante:
        return jsonify({"error": "Estudiante no encontrado"}), 404

    matriculas = Matricula.query.filter_by(estudiante_id=estudiante.id, estado_id=3).all()
    return jsonify([
        {
            "id": m.id,
            "periodo_academico_nombre": m.periodo_academico.nombre if m.periodo_academico else "—",
            "semestre_codigo": m.semestre.codigo if m.semestre else "—",
            "estado_nombre": m.estado.nombre if m.estado else "—",
            "pagado": m.pagado,
            "fecha_creacion": m.created_at.isoformat() if hasattr(m, "created_at") and m.created_at else None,
        }
        for m in matriculas
    ])


def descargar_comprobante(matricula_id):
    token = request.args.get("token")
    if token:
        request.environ["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    try:
        verify_jwt_in_request()
    except Exception:
        return jsonify({"error": "Autenticaci\u00f3n requerida"}), 401

    matricula = db.session.get(Matricula, matricula_id)
    if not matricula or not matricula.comprobante_path:
        return jsonify({"error": "Comprobante no encontrado"}), 404
    if not os.path.exists(matricula.comprobante_path):
        return jsonify({"error": "Archivo no encontrado en el servidor"}), 404
    return send_file(
        matricula.comprobante_path,
        as_attachment=True,
        download_name=os.path.basename(matricula.comprobante_path),
    )


def cursos_disponibles():
    usuario_id = int(get_jwt_identity())
    periodo = MatriculaService.periodo_actual()

    resultado, error = MatriculaService.cursos_disponibles(usuario_id, periodo.id)

    if error:
        return jsonify({"error": error}), 400

    return jsonify(resultado)
