from app import db
from app.modelos.curso import Curso

def ejecutar():
    if Curso.query.count() > 5:
        print("Cursos ya existen")
        return

    cursos = [
        Curso(nombre="Programacin I", codigo="PROG1", creditos=4, horas_lectivas=4, horas_practicas=2),
        Curso(nombre="Base de Datos I", codigo="BD1", creditos=4, horas_lectivas=3, horas_practicas=2),
        Curso(nombre="Redes de Computadoras", codigo="RED1", creditos=3, horas_lectivas=3, horas_practicas=1),
        Curso(nombre="Clculo I", codigo="CALC1", creditos=4, horas_lectivas=4, horas_practicas=2),
        Curso(nombre="Clculo II", codigo="CALC2", creditos=4, horas_lectivas=4, horas_practicas=2),
        Curso(nombre="Fsica I", codigo="FIS1", creditos=4, horas_lectivas=3, horas_practicas=3),
        Curso(nombre="Fsica II", codigo="FIS2", creditos=4, horas_lectivas=3, horas_practicas=3),
        Curso(nombre="Lenguaje y Comunicacin", codigo="LENG1", creditos=3, horas_lectivas=3, horas_practicas=0),
        Curso(nombre="Algoritmos y Estructura de Datos", codigo="ALGO1", creditos=4, horas_lectivas=4, horas_practicas=2),
        Curso(nombre="Ingeniera de Requisitos", codigo="REQ1", creditos=3, horas_lectivas=3, horas_practicas=1),
        Curso(nombre="Diseo de Interfaces", codigo="UXUI1", creditos=3, horas_lectivas=2, horas_practicas=2),
        Curso(nombre="Sistemas Operativos", codigo="SO1", creditos=4, horas_lectivas=4, horas_practicas=2),
        Curso(nombre="Inteligencia Artificial", codigo="IA1", creditos=4, horas_lectivas=4, horas_practicas=2),
        Curso(nombre="Seguridad Informtica", codigo="SEG1", creditos=4, horas_lectivas=4, horas_practicas=2),
        Curso(nombre="Metodologas giles", codigo="AGIL1", creditos=3, horas_lectivas=3, horas_practicas=0),
    ]

    for c in cursos:
        if not Curso.query.filter_by(codigo=c.codigo).first():
            db.session.add(c)
            
    db.session.commit()
    print("Cursos creados")
