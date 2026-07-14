from app import db
from app.modelos.estado_matricula import EstadoMatricula
from app.modelos.estudiante import Estudiante
from app.modelos.matricula import Matricula
from app.modelos.periodo_academico import PeriodoAcademico
from app.modelos.semestre import Semestre

def ejecutar():
    if Matricula.query.count() > 5:
        print("Matriculas ya existen en masa")
        return

    estudiantes = Estudiante.query.all()
    periodo = PeriodoAcademico.query.first()
    semestres = Semestre.query.all()
    estado = EstadoMatricula.query.filter_by(nombre="Matriculado").first()

    if not estudiantes or not periodo or not semestres or not estado:
        print("Faltan datos para matriculas masivas")
        return

    nuevas = 0
    for i, est in enumerate(estudiantes):
        # Asignar un semestre aleatorio basado en su ID para variar
        semestre = semestres[i % min(len(semestres), 4)] 
        
        # Verificar si ya tiene matricula este periodo
        existe = Matricula.query.filter_by(estudiante_id=est.id, periodo_academico_id=periodo.id).first()
        if not existe:
            mat = Matricula(
                estudiante_id=est.id,
                periodo_academico_id=periodo.id,
                semestre_id=semestre.id,
                estado_id=estado.id
            )
            db.session.add(mat)
            nuevas += 1

    db.session.commit()
    print(f"Matriculas masivas creadas: {nuevas}")
