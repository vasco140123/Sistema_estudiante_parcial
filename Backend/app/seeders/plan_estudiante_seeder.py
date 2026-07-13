from app import db
from app.modelos.estudiante import Estudiante
from app.modelos.plan_de_estudios import PlanDeEstudios
from app.modelos.plan_estudiante import PlanEstudiante
from app.modelos.semestre import Semestre


def ejecutar():
    if PlanEstudiante.query.first():
        print("Planes de estudiante ya existen")
        return

    estudiante = Estudiante.query.first()
    plan = PlanDeEstudios.query.first()
    semestre = Semestre.query.first()

    if not estudiante or not plan:
        print("No hay estudiante o plan de estudios para crear plan_estudiante")
        return

    plan_estudiante = PlanEstudiante(
        estudiante_id=estudiante.id,
        plan_estudios_id=plan.id,
        semestre_id=semestre.id if semestre else None,
    )

    db.session.add(plan_estudiante)
    db.session.commit()

    print("Planes de estudiante creados")
