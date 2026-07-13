from app import db
from app.modelos.curso import Curso
from app.modelos.plan_cursos_semestre import PlanCursosSemestre
from app.modelos.plan_de_estudios import PlanDeEstudios
from app.modelos.semestre import Semestre


def ejecutar():
    if PlanCursosSemestre.query.first():
        print("Eliminando plan cursos semestre existente...")
        PlanCursosSemestre.query.delete()
        db.session.commit()

    planes = PlanDeEstudios.query.all()
    cursos = Curso.query.order_by(Curso.id).all()
    semestres = Semestre.query.order_by(Semestre.id).all()

    if not planes or not cursos or not semestres:
        print("No hay planes, cursos o semestres suficientes para crear plan_cursos_semestre")
        return

    cursos_por_semestre = 3
    asignaciones = []

    for plan in planes:
        for idx, curso in enumerate(cursos):
            sem_index = idx // cursos_por_semestre
            if sem_index >= len(semestres):
                break
            asignaciones.append(
                PlanCursosSemestre(
                    plan_estudios_id=plan.id,
                    semestre_id=semestres[sem_index].id,
                    curso_id=curso.id,
                )
            )

    db.session.add_all(asignaciones)
    db.session.commit()

    print(f"Plan cursos semestre creado: {len(asignaciones)} asignaciones para {len(planes)} plan(es)")
