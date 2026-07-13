from datetime import datetime
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from app import bcrypt
from app import db
from app.modelos.facultad import Facultad
from app.modelos.especialidad import Especialidad
from app.modelos.plan_de_estudios import PlanDeEstudios
from app.modelos.plan_estudiante import PlanEstudiante
from app.modelos.plan_cursos_semestre import PlanCursosSemestre
from app.modelos.periodo_academico import PeriodoAcademico
from app.modelos.semestre import Semestre
from app.modelos.curso import Curso
from app.modelos.seccion_curso import SeccionCurso
from app.modelos.usuario import Usuario
from app.modelos.auditoria import Auditoria
from app.modelos.matricula import Matricula
from app.modelos.estudiante import Estudiante
from app.modelos.docente import Docente
from app.modelos.matricula_detalle import MatriculaDetalle
from app.modelos.certificado import Certificado


def listar_facultades():
    facultades = Facultad.query.all()
    return jsonify([
        {"id": f.id, "nombre": f.nombre}
        for f in facultades
    ])


def listar_especialidades():
    especialidades = Especialidad.query.all()
    return jsonify([
        {
            "id": e.id,
            "nombre": e.nombre,
            "facultad_id": e.facultad_id
        }
        for e in especialidades
    ])


def listar_planes_estudio():
    planes = PlanDeEstudios.query.all()
    return jsonify([
        {
            "id": p.id,
            "especialidad_id": p.especialidad_id,
            "especialidad_nombre": p.especialidad.nombre if p.especialidad else None,
            "anio_creacion": p.anio_creacion,
            "vigente": p.vigente,
            "nombre": f"Plan {p.anio_creacion} ({p.especialidad.nombre})" if p.especialidad else f"Plan {p.anio_creacion}",
        }
        for p in planes
    ])


def listar_semestres():
    semestres = Semestre.query.all()
    return jsonify([
        {"id": s.id, "codigo": s.codigo}
        for s in semestres
    ])


def listar_periodos():
    periodos = PeriodoAcademico.query.order_by(PeriodoAcademico.fecha_inicio.desc()).all()
    return jsonify([
        {
            "id": p.id,
            "nombre": p.nombre,
            "fecha_inicio": p.fecha_inicio.isoformat() if p.fecha_inicio else None,
            "fecha_fin": p.fecha_fin.isoformat() if p.fecha_fin else None,
        }
        for p in periodos
    ])


def _datos_usuario(u):
    perfil = None
    plan_estudios_id = None
    plan_estudios_id = None
    plan_estudios_nombre = None
    semestre_id = None
    semestre_codigo = None
    if u.rol == "estudiante":
        est = Estudiante.query.filter_by(usuario_id=u.id).first()
        if est:
            pe = PlanEstudiante.query.filter_by(estudiante_id=est.id).first()
            if pe:
                plan_estudios_id = pe.plan_estudios_id
                plan_estudios_nombre = f"Plan {pe.plan_estudios.anio_creacion} ({pe.plan_estudios.especialidad.nombre})" if pe.plan_estudios and pe.plan_estudios.especialidad else f"Plan {pe.plan_estudios.anio_creacion}" if pe.plan_estudios else None
                semestre_id = pe.semestre_id
                semestre_codigo = pe.semestre.codigo if pe.semestre else None
            perfil = {
                "id": est.id,
                "nombres": est.nombres,
                "apellido_paterno": est.apellido_paterno,
                "apellido_materno": est.apellido_materno,
                "correo_institucional": est.correo_institucional,
                "especialidad_id": est.especialidad_id,
                "plan_estudios_id": plan_estudios_id,
                "plan_estudios_nombre": plan_estudios_nombre,
                "semestre_id": semestre_id,
                "semestre_codigo": semestre_codigo,
            }
    elif u.rol == "docente":
        doc = Docente.query.filter_by(usuario_id=u.id).first()
        if doc:
            perfil = {
                "id": doc.id,
                "nombres": doc.nombres,
                "apellido_paterno": doc.apellido_paterno,
                "apellido_materno": doc.apellido_materno,
                "correo_institucional": doc.correo_institucional,
            }
    return {
        "id": u.id,
        "username": u.username,
        "rol": u.rol,
        "activo": u.deleted_at is None,
        "perfil": perfil,
    }


def listar_usuarios():
    incluir_inactivos = request.args.get("incluir_inactivos", "").lower() == "true"
    query = Usuario.query
    if not incluir_inactivos:
        query = query.filter(Usuario.deleted_at.is_(None))
    usuarios = query.order_by(Usuario.id).all()
    return jsonify([_datos_usuario(u) for u in usuarios])


def detalle_usuario(usuario_id):
    usuario = db.session.get(Usuario, usuario_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify(_datos_usuario(usuario))


def actualizar_usuario(usuario_id):
    usuario = db.session.get(Usuario, usuario_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    data = request.get_json()
    username = data.get("username", "").strip()
    if username and username != usuario.username:
        if Usuario.query.filter_by(username=username).first():
            return jsonify({"error": "El nombre de usuario ya está en uso"}), 400
        usuario.username = username

    rol = data.get("rol")
    if rol and rol in ["estudiante", "docente", "administrador", "direccion"]:
        usuario.rol = rol
    usuario.modified_at = datetime.now()

    if usuario.rol == "estudiante":
        est = Estudiante.query.filter_by(usuario_id=usuario.id).first()
        if est:
            for campo in ["nombres", "apellido_paterno", "apellido_materno", "correo_institucional"]:
                val = data.get(campo, "").strip()
                if val:
                    setattr(est, campo, val)
            dni = data.get("dni", "").strip()
            if dni:
                est.dni = dni
            especialidad_id = data.get("especialidad_id")
            if especialidad_id:
                est.especialidad_id = especialidad_id
            est.modified_at = datetime.now()

        plan_estudios_id = data.get("plan_estudios_id")
        if plan_estudios_id:
            pe = PlanEstudiante.query.filter_by(estudiante_id=est.id).first()
            semestre_id = data.get("semestre_id")
            if pe:
                pe.plan_estudios_id = plan_estudios_id
                pe.semestre_id = semestre_id or None
                pe.modified_at = datetime.now()
            else:
                pe = PlanEstudiante(
                    estudiante_id=est.id,
                    plan_estudios_id=plan_estudios_id,
                    semestre_id=semestre_id or None,
                    created_at=datetime.now(),
                )
                db.session.add(pe)

    elif usuario.rol == "docente":
        doc = Docente.query.filter_by(usuario_id=usuario.id).first()
        if doc:
            for campo in ["nombres", "apellido_paterno", "apellido_materno", "correo_institucional"]:
                val = data.get(campo, "").strip()
                if val:
                    setattr(doc, campo, val)
            doc.modified_at = datetime.now()

    Auditoria.registrar(
        usuario_id=int(get_jwt_identity()),
        accion="actualizacion_usuario",
        detalle=f"Actualizó usuario #{usuario_id}",
    )
    db.session.commit()
    return jsonify({"mensaje": "Usuario actualizado correctamente", "usuario": _datos_usuario(usuario)})


def eliminar_usuario(usuario_id):
    admin_id = int(get_jwt_identity())
    if admin_id == usuario_id:
        return jsonify({"error": "No puedes eliminar tu propio usuario"}), 400

    usuario = db.session.get(Usuario, usuario_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    from app.modelos.plan_estudiante import PlanEstudiante
    from app.modelos.progreso_estudiante import ProgresoEstudiante
    from app.modelos.expediente_semestral import ExpedienteSemestral
    from app.modelos.historial_merito import HistorialMerito
    from app.modelos.certificado import Certificado
    from app.modelos.seccion_docente import SeccionDocente

    estudiante = Estudiante.query.filter_by(usuario_id=usuario_id).first()
    if estudiante:
        PlanEstudiante.query.filter_by(estudiante_id=estudiante.id).delete()
        ProgresoEstudiante.query.filter_by(estudiante_id=estudiante.id).delete()
        ExpedienteSemestral.query.filter_by(estudiante_id=estudiante.id).delete()
        HistorialMerito.query.filter_by(estudiante_id=estudiante.id).delete()
        Certificado.query.filter_by(estudiante_id=estudiante.id).delete()
        Matricula.query.filter_by(estudiante_id=estudiante.id).delete()
        db.session.delete(estudiante)

    docente = Docente.query.filter_by(usuario_id=usuario_id).first()
    if docente:
        SeccionDocente.query.filter_by(docente_id=docente.id).delete()
        db.session.delete(docente)

    db.session.delete(usuario)
    Auditoria.registrar(
        usuario_id=admin_id,
        accion="eliminacion_usuario",
        detalle=f"Eliminó usuario '{usuario.username}' permanentemente",
    )
    db.session.commit()
    return jsonify({"mensaje": f"Usuario '{usuario.username}' eliminado permanentemente"})


def crear_usuario():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")
    rol = data.get("rol", "").strip()

    if not username or not password or not rol:
        return jsonify({"error": "Faltan campos requeridos: username, password, rol"}), 400

    roles_validos = ["estudiante", "docente", "administrador", "direccion"]
    if rol not in roles_validos:
        return jsonify({"error": f"Rol inválido. Debe ser uno de: {roles_validos}"}), 400

    if Usuario.query.filter_by(username=username).first():
        return jsonify({"error": "El nombre de usuario ya está en uso"}), 400

    if len(password) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400

    usuario = Usuario(
        username=username,
        password=bcrypt.generate_password_hash(password).decode("utf-8"),
        rol=rol,
        created_at=datetime.now(),
    )
    db.session.add(usuario)
    db.session.flush()

    mensaje_extra = None
    if rol == "estudiante":
        nombres = data.get("nombres", "").strip()
        apellido_paterno = data.get("apellido_paterno", "").strip()
        apellido_materno = data.get("apellido_materno", "").strip()
        correo_institucional = data.get("correo_institucional", "").strip()
        especialidad_id = data.get("especialidad_id")
        dni = data.get("dni", "").strip()

        faltantes = []
        if not nombres: faltantes.append("nombres")
        if not apellido_paterno: faltantes.append("apellido_paterno")
        if not apellido_materno: faltantes.append("apellido_materno")
        if not correo_institucional: faltantes.append("correo_institucional")
        if not especialidad_id: faltantes.append("especialidad_id")
        if not dni: faltantes.append("dni")
        if faltantes:
            db.session.rollback()
            return jsonify({"error": f"Faltan campos para estudiante: {faltantes}"}), 400

        estudiante = Estudiante(
            usuario_id=usuario.id,
            especialidad_id=especialidad_id,
            nombres=nombres,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            correo_institucional=correo_institucional,
            dni=dni,
        )
        db.session.add(estudiante)
        db.session.flush()
        mensaje_extra = f"Perfil de estudiante creado (ID: {estudiante.id})"

        plan_estudios_id = data.get("plan_estudios_id")
        if plan_estudios_id:
            plan = db.session.get(PlanDeEstudios, plan_estudios_id)
            if plan:
                semestre_id = data.get("semestre_id")
                pe = PlanEstudiante(
                    estudiante_id=estudiante.id,
                    plan_estudios_id=plan_estudios_id,
                    semestre_id=semestre_id or None,
                    created_at=datetime.now(),
                )
                db.session.add(pe)
                mensaje_extra += f", plan de estudios asignado"

    elif rol == "docente":
        nombres = data.get("nombres", "").strip()
        apellido_paterno = data.get("apellido_paterno", "").strip()
        apellido_materno = data.get("apellido_materno", "").strip()
        correo_institucional = data.get("correo_institucional", "").strip()

        faltantes = []
        if not nombres: faltantes.append("nombres")
        if not apellido_paterno: faltantes.append("apellido_paterno")
        if not apellido_materno: faltantes.append("apellido_materno")
        if not correo_institucional: faltantes.append("correo_institucional")
        if faltantes:
            db.session.rollback()
            return jsonify({"error": f"Faltan campos para docente: {faltantes}"}), 400

        docente = Docente(
            usuario_id=usuario.id,
            nombres=nombres,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            correo_institucional=correo_institucional,
        )
        db.session.add(docente)
        mensaje_extra = f"Perfil de docente creado (ID: {docente.id})"

    admin_id = int(get_jwt_identity())
    Auditoria.registrar(
        usuario_id=admin_id,
        accion="creacion_usuario",
        detalle=f"Creó usuario '{username}' con rol '{rol}'"
    )
    db.session.commit()

    return jsonify({
        "mensaje": f"Usuario '{username}' creado correctamente",
        "detalle": mensaje_extra,
        "usuario": _datos_usuario(usuario),
    }), 201


def toggle_usuario(usuario_id):
    admin_id = int(get_jwt_identity())
    if admin_id == usuario_id:
        return jsonify({"error": "No puedes desactivar tu propio usuario"}), 400

    usuario = db.session.get(Usuario, usuario_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    if usuario.deleted_at is None:
        usuario.deleted_at = datetime.now()
        accion = "desactivacion_usuario"
        mensaje = f"Usuario '{usuario.username}' desactivado"
    else:
        usuario.deleted_at = None
        accion = "activacion_usuario"
        mensaje = f"Usuario '{usuario.username}' activado"

    Auditoria.registrar(
        usuario_id=admin_id,
        accion=accion,
        detalle=f"{accion.replace('_', ' ')} '{usuario.username}'"
    )
    db.session.commit()

    return jsonify({"mensaje": mensaje, "usuario": _datos_usuario(usuario)})


def cambiar_password(usuario_id):
    data = request.get_json()
    nueva_password = data.get("password", "")

    if not nueva_password or len(nueva_password) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400

    usuario = db.session.get(Usuario, usuario_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    usuario.password = bcrypt.generate_password_hash(nueva_password).decode("utf-8")

    admin_id = int(get_jwt_identity())
    Auditoria.registrar(
        usuario_id=admin_id,
        accion="cambio_password",
        detalle=f"Cambió la contraseña del usuario '{usuario.username}'"
    )
    db.session.commit()

    return jsonify({"mensaje": "Contraseña actualizada correctamente"})


def cambiar_rol(usuario_id):
    data = request.get_json()
    nuevo_rol = data.get("rol")

    roles_validos = ["estudiante", "docente", "administrador", "direccion"]
    if nuevo_rol not in roles_validos:
        return jsonify({"error": f"Rol inválido. Debe ser uno de: {roles_validos}"}), 400

    usuario = db.session.get(Usuario, usuario_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    rol_anterior = usuario.rol
    usuario.rol = nuevo_rol

    admin_id = int(get_jwt_identity())
    Auditoria.registrar(
        usuario_id=admin_id,
        accion="cambio_de_rol",
        detalle=f"Usuario '{usuario.username}' cambió de '{rol_anterior}' a '{nuevo_rol}'"
    )
    db.session.commit()

    return jsonify({"mensaje": "Rol actualizado correctamente", "usuario": _datos_usuario(usuario)})


def registrar_docente():
    data = request.get_json()

    campos_requeridos = ["username", "password", "nombres", "apellido_paterno", "apellido_materno", "correo_institucional"]
    faltantes = [campo for campo in campos_requeridos if not data.get(campo)]

    if faltantes:
        return jsonify({"error": f"Faltan campos requeridos: {faltantes}"}), 400

    username = data.get("username")
    if Usuario.query.filter_by(username=username).first():
        return jsonify({"error": "El nombre de usuario ya está en uso"}), 400

    usuario = Usuario(
        username=username,
        password=bcrypt.generate_password_hash(data.get("password")).decode("utf-8"),
        rol="docente",
    )
    db.session.add(usuario)
    db.session.flush()

    docente = Docente(
        usuario_id=usuario.id,
        nombres=data.get("nombres"),
        apellido_paterno=data.get("apellido_paterno"),
        apellido_materno=data.get("apellido_materno"),
        correo_institucional=data.get("correo_institucional"),
    )
    db.session.add(docente)
    db.session.commit()

    admin_id = int(get_jwt_identity())
    Auditoria.registrar(
        usuario_id=admin_id,
        accion="creacion_usuario",
        detalle=f"Registró docente '{username}'"
    )
    db.session.commit()

    return jsonify({
        "mensaje": "Docente registrado correctamente",
        "usuario_id": usuario.id,
        "docente_id": docente.id,
    }), 201


def crear_plan_estudio():
    data = request.get_json()
    especialidad_id = data.get("especialidad_id")
    anio_creacion = data.get("anio_creacion")

    if not especialidad_id or not anio_creacion:
        return jsonify({"error": "especialidad_id y anio_creacion son requeridos"}), 400

    plan = PlanDeEstudios(
        especialidad_id=especialidad_id,
        anio_creacion=anio_creacion,
        vigente=True,
        created_at=datetime.now(),
    )
    db.session.add(plan)
    db.session.flush()

    Auditoria.registrar(
        usuario_id=int(get_jwt_identity()),
        accion="creacion_plan_estudio",
        detalle=f"Creó plan de estudios #{plan.id} para especialidad #{especialidad_id}",
    )
    db.session.commit()
    return jsonify({"mensaje": "Plan de estudios creado", "plan": {
        "id": plan.id,
        "especialidad_id": plan.especialidad_id,
        "anio_creacion": plan.anio_creacion,
        "vigente": plan.vigente,
    }}), 201


def actualizar_plan_estudio(plan_id):
    plan = db.session.get(PlanDeEstudios, plan_id)
    if not plan:
        return jsonify({"error": "Plan de estudios no encontrado"}), 404

    data = request.get_json()
    if "especialidad_id" in data:
        plan.especialidad_id = data["especialidad_id"]
    if "anio_creacion" in data:
        plan.anio_creacion = data["anio_creacion"]
    if "vigente" in data:
        plan.vigente = data["vigente"]
    plan.modified_at = datetime.now()

    Auditoria.registrar(
        usuario_id=int(get_jwt_identity()),
        accion="actualizacion_plan_estudio",
        detalle=f"Actualizó plan de estudios #{plan_id}",
    )
    db.session.commit()
    return jsonify({"mensaje": "Plan de estudios actualizado", "plan": {
        "id": plan.id,
        "especialidad_id": plan.especialidad_id,
        "especialidad_nombre": plan.especialidad.nombre if plan.especialidad else None,
        "anio_creacion": plan.anio_creacion,
        "vigente": plan.vigente,
        "nombre": f"Plan {plan.anio_creacion} ({plan.especialidad.nombre})" if plan.especialidad else f"Plan {plan.anio_creacion}",
    }})


def eliminar_plan_estudio(plan_id):
    plan = db.session.get(PlanDeEstudios, plan_id)
    if not plan:
        return jsonify({"error": "Plan de estudios no encontrado"}), 404

    tiene_estudiantes = PlanEstudiante.query.filter_by(plan_estudios_id=plan_id).first()
    if tiene_estudiantes:
        return jsonify({"error": "No se puede eliminar: hay estudiantes asignados a este plan"}), 400

    db.session.delete(plan)
    Auditoria.registrar(
        usuario_id=int(get_jwt_identity()),
        accion="eliminacion_plan_estudio",
        detalle=f"Eliminó plan de estudios #{plan_id}",
    )
    db.session.commit()
    return jsonify({"mensaje": "Plan de estudios eliminado"})


def listar_cursos_plan(plan_id):
    plan = db.session.get(PlanDeEstudios, plan_id)
    if not plan:
        return jsonify({"error": "Plan de estudios no encontrado"}), 404
    cursos = PlanCursosSemestre.query.filter_by(plan_estudios_id=plan_id).all()
    return jsonify([
        {
            "id": c.id,
            "plan_estudios_id": c.plan_estudios_id,
            "semestre_id": c.semestre_id,
            "semestre_codigo": c.semestre.codigo if c.semestre else None,
            "curso_id": c.curso_id,
            "curso_nombre": c.curso.nombre if c.curso else None,
            "curso_codigo": c.curso.codigo if c.curso else None,
            "creditos": c.curso.creditos if c.curso else None,
        }
        for c in cursos
    ])


def asignar_curso_plan(plan_id):
    plan = db.session.get(PlanDeEstudios, plan_id)
    if not plan:
        return jsonify({"error": "Plan de estudios no encontrado"}), 404

    data = request.get_json()
    semestre_id = data.get("semestre_id")
    curso_id = data.get("curso_id")

    if not semestre_id or not curso_id:
        return jsonify({"error": "semestre_id y curso_id son requeridos"}), 400

    if db.session.get(Curso, curso_id) is None:
        return jsonify({"error": "Curso no encontrado"}), 404

    existe = PlanCursosSemestre.query.filter_by(
        plan_estudios_id=plan_id, semestre_id=semestre_id, curso_id=curso_id
    ).first()
    if existe:
        return jsonify({"error": "El curso ya está asignado a ese semestre en este plan"}), 400

    pcs = PlanCursosSemestre(
        plan_estudios_id=plan_id,
        semestre_id=semestre_id,
        curso_id=curso_id,
        created_at=datetime.now(),
    )
    db.session.add(pcs)
    db.session.flush()

    from app.modulos.matricula.services import MatriculaService
    periodo = MatriculaService.periodo_actual()
    seccion_existente = SeccionCurso.query.filter_by(
        periodo_academico_id=periodo.id,
        curso_id=curso_id,
        semestre_id=semestre_id,
    ).first()
    if not seccion_existente:
        seccion = SeccionCurso(
            periodo_academico_id=periodo.id,
            curso_id=curso_id,
            semestre_id=semestre_id,
            cupos=40,
        )
        db.session.add(seccion)

    Auditoria.registrar(
        usuario_id=int(get_jwt_identity()),
        accion="asignar_curso_plan",
        detalle=f"Asignó curso #{curso_id} al plan #{plan_id}, semestre #{semestre_id}",
    )
    db.session.commit()
    return jsonify({"mensaje": "Curso asignado al plan", "id": pcs.id}), 201


def eliminar_curso_plan(pcs_id):
    pcs = db.session.get(PlanCursosSemestre, pcs_id)
    if not pcs:
        return jsonify({"error": "Asignación no encontrada"}), 404

    db.session.delete(pcs)
    Auditoria.registrar(
        usuario_id=int(get_jwt_identity()),
        accion="eliminar_curso_plan",
        detalle=f"Eliminó asignación #{pcs_id} (curso #{pcs.curso_id} del plan #{pcs.plan_estudios_id})",
    )
    db.session.commit()
    return jsonify({"mensaje": "Curso eliminado del plan"})


def listar_auditorias():
    query = Auditoria.query

    accion = request.args.get("accion")
    if accion:
        query = query.filter(Auditoria.accion == accion)

    fecha_desde = request.args.get("fecha_desde")
    if fecha_desde:
        query = query.filter(Auditoria.created_at >= fecha_desde)

    fecha_hasta = request.args.get("fecha_hasta")
    if fecha_hasta:
        query = query.filter(Auditoria.created_at <= fecha_hasta + " 23:59:59")

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 30, type=int)
    per_page = min(per_page, 100)

    total = query.count()
    registros = query.order_by(Auditoria.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

    acciones_disponibles = db.session.query(Auditoria.accion).distinct().all()
    acciones_disponibles = sorted([a[0] for a in acciones_disponibles])

    items = []
    for a in registros:
        username = a.usuario.username if a.usuario else "—"
        items.append({
            "id": a.id,
            "usuario_id": a.usuario_id,
            "usuario_username": username,
            "accion": a.accion,
            "detalle": a.detalle,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        })

    return jsonify({
        "items": items,
        "total": total,
        "page": page,
        "pages": (total + per_page - 1) // per_page,
        "filtros": {
            "acciones": acciones_disponibles,
        }
    })


def reportes_estrategicos():
    total_estudiantes = Estudiante.query.count()
    total_docentes = Docente.query.count()
    total_matriculas = Matricula.query.count()
    matriculas_confirmadas = Matricula.query.filter_by(estado_id=3).count()

    detalles_con_nota = MatriculaDetalle.query.filter(MatriculaDetalle.nota_final.isnot(None)).all()
    promedio_institucional = None
    if detalles_con_nota:
        suma = sum(float(d.nota_final) for d in detalles_con_nota)
        promedio_institucional = round(suma / len(detalles_con_nota), 2)

    certificados_emitidos = Certificado.query.filter_by(estado="Emitido").count()
    certificados_pendientes = Certificado.query.filter(Certificado.estado != "Emitido").count()

    return jsonify({
        "poblacion": {
            "total_estudiantes": total_estudiantes,
            "total_docentes": total_docentes
        },
        "matricula": {
            "total_solicitudes": total_matriculas,
            "confirmadas": matriculas_confirmadas
        },
        "academico": {
            "promedio_institucional": promedio_institucional
        },
        "certificados": {
            "emitidos": certificados_emitidos,
            "pendientes": certificados_pendientes
        }
    })


def asignar_plan_estudiante(estudiante_id):
    data = request.get_json()
    plan_estudios_id = data.get("plan_estudios_id")

    if not plan_estudios_id:
        return jsonify({"error": "plan_estudios_id es requerido"}), 400

    estudiante = db.session.get(Estudiante, estudiante_id)
    if not estudiante:
        return jsonify({"error": "Estudiante no encontrado"}), 404

    plan = db.session.get(PlanDeEstudios, plan_estudios_id)
    if not plan:
        return jsonify({"error": "Plan de estudios no encontrado"}), 404

    pe = PlanEstudiante.query.filter_by(estudiante_id=estudiante_id).first()
    semestre_id = data.get("semestre_id")
    if pe:
        pe.plan_estudios_id = plan_estudios_id
        pe.semestre_id = semestre_id or None
        pe.modified_at = datetime.now()
        mensaje = "Plan de estudios actualizado"
    else:
        pe = PlanEstudiante(
            estudiante_id=estudiante_id,
            plan_estudios_id=plan_estudios_id,
            semestre_id=semestre_id or None,
            created_at=datetime.now(),
        )
        db.session.add(pe)
        mensaje = "Plan de estudios asignado"

    Auditoria.registrar(
        usuario_id=int(get_jwt_identity()),
        accion="asignar_plan_estudio",
        detalle=f"Plan #{plan_estudios_id} asignado a estudiante #{estudiante_id}",
    )
    db.session.commit()
    return jsonify({"mensaje": mensaje, "plan_estudios_id": plan_estudios_id})


def obtener_configuracion_ciclo():
    from app.modelos.configuracion_ciclo_global import ConfiguracionCicloGlobal
    from app.utils.ciclo_academico import ESTADOS_CICLO

    config = db.session.get(ConfiguracionCicloGlobal, 1)
    if not config:
        config = ConfiguracionCicloGlobal(id=1, estado_ciclo=ESTADOS_CICLO[0])
        db.session.add(config)
        db.session.commit()

    return jsonify({
        "id": config.id,
        "periodo_academico_id": config.periodo_academico_id,
        "estado_ciclo": config.estado_ciclo,
        "fecha_cierre_matricula": config.fecha_cierre_matricula.isoformat() if config.fecha_cierre_matricula else None,
        "fecha_limite_notas": config.fecha_limite_notas.isoformat() if config.fecha_limite_notas else None,
        "fecha_cierre_actas": config.fecha_cierre_actas.isoformat() if config.fecha_cierre_actas else None,
        "estados_disponibles": ESTADOS_CICLO,
    })


def actualizar_configuracion_ciclo():
    from datetime import datetime
    from app.modelos.configuracion_ciclo_global import ConfiguracionCicloGlobal

    data = request.get_json()
    config = db.session.get(ConfiguracionCicloGlobal, 1)
    if not config:
        return jsonify({"error": "Configuración no encontrada"}), 404

    if "periodo_academico_id" in data:
        config.periodo_academico_id = data["periodo_academico_id"]
    if "estado_ciclo" in data:
        config.estado_ciclo = data["estado_ciclo"]
    if "fecha_cierre_matricula" in data and data["fecha_cierre_matricula"]:
        config.fecha_cierre_matricula = datetime.fromisoformat(data["fecha_cierre_matricula"])
    if "fecha_limite_notas" in data and data["fecha_limite_notas"]:
        config.fecha_limite_notas = datetime.fromisoformat(data["fecha_limite_notas"])
    if "fecha_cierre_actas" in data and data["fecha_cierre_actas"]:
        config.fecha_cierre_actas = datetime.fromisoformat(data["fecha_cierre_actas"])

    db.session.commit()
    return jsonify({"mensaje": "Configuración de ciclo actualizada correctamente"})