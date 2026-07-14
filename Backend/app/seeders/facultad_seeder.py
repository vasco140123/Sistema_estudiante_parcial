from app import db
from app.modelos.facultad import Facultad

def ejecutar():
    if Facultad.query.first():
        print("Facultades ya existen")
        return

    facultades = [
        Facultad(nombre="Facultad de Ingeniera de Sistemas"),
        Facultad(nombre="Facultad de Ingeniera en Ciberseguridad"),
        Facultad(nombre="Facultad de Ingeniera Electrnica"),
        Facultad(nombre="Facultad de Ciencias de la Salud"),
        Facultad(nombre="Facultad de Ciencias Empresariales"),
    ]

    db.session.add_all(facultades)
    db.session.commit()
    print("Facultades creadas")
