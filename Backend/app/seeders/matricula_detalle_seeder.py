import random
from app import db
from app.modelos.estado_curso import EstadoCurso
from app.modelos.matricula import Matricula
from app.modelos.matricula_detalle import MatriculaDetalle
from app.modelos.seccion_curso import SeccionCurso
from app.modelos.plan_cursos_semestre import PlanCursosSemestre
from app.modelos.plan_estudiante import PlanEstudiante

def ejecutar():
    if MatriculaDetalle.query.count() > 20:
        print("Detalles de matricula ya existen en masa")
        return

    matriculas = Matricula.query.all()
    estado_aprobado = EstadoCurso.query.filter_by(nombre="Aprobado").first()
    estado_desaprobado = EstadoCurso.query.filter_by(nombre="Desaprobado").first()

    if not matriculas or not estado_aprobado or not estado_desaprobado:
        print("Faltan datos para detalles de matricula")
        return

    creados = 0
    for mat in matriculas:
        plan_estudiante = PlanEstudiante.query.filter_by(estudiante_id=mat.estudiante_id).first()
        if not plan_estudiante: continue

        # Buscar todos los cursos de su plan para el semestre matriculado
        cursos_plan = PlanCursosSemestre.query.filter_by(
            plan_estudios_id=plan_estudiante.plan_estudios_id,
            semestre_id=mat.semestre_id
        ).all()

        for cp in cursos_plan:
            seccion = SeccionCurso.query.filter_by(
                curso_id=cp.curso_id,
                semestre_id=cp.semestre_id
            ).first()
            
            if seccion:
                existe = MatriculaDetalle.query.filter_by(matricula_id=mat.id, seccion_curso_id=seccion.id).first()
                if not existe:
                    nota = round(random.uniform(9.0, 18.0), 2)
                    estado_id = estado_aprobado.id if nota >= 10.5 else estado_desaprobado.id
                    
                    detalle = MatriculaDetalle(
                        matricula_id=mat.id,
                        seccion_curso_id=seccion.id,
                        nota_final=nota,
                        estado_curso_id=estado_id,
                    )
                    db.session.add(detalle)
                    creados += 1
    
    db.session.commit()
    print(f"Detalles de matricula generados: {creados} (con notas aleatorias)")
