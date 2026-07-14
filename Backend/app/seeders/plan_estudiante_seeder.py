from app import db
from app.modelos.estudiante import Estudiante
from app.modelos.plan_de_estudios import PlanDeEstudios
from app.modelos.plan_estudiante import PlanEstudiante

def ejecutar():
    if PlanEstudiante.query.count() > 5:
        print("Planes de estudiante masivos ya existen")
        return

    estudiantes = Estudiante.query.all()
    planes = PlanDeEstudios.query.all()

    if not estudiantes or not planes:
        return

    creados = 0
    for est in estudiantes:
        existe = PlanEstudiante.query.filter_by(estudiante_id=est.id).first()
        if not existe:
            # Asignar un plan basado en su especialidad si es posible, sino el primero
            plan = PlanDeEstudios.query.filter_by(especialidad_id=est.especialidad_id).first()
            if not plan:
                plan = planes[0]
                
            pe = PlanEstudiante(
                estudiante_id=est.id,
                plan_estudios_id=plan.id,
                estado="Activo"
            )
            db.session.add(pe)
            creados += 1

    db.session.commit()
    print(f"Planes de estudiante asignados masivamente: {creados}")
