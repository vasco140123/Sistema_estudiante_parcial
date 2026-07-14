from app import db
from app.modelos.especialidad import Especialidad
from app.modelos.facultad import Facultad

def ejecutar():
    if Especialidad.query.first():
        print("Especialidades ya existen")
        return

    sistemas = Facultad.query.filter_by(nombre="Facultad de Ingeniera de Sistemas").first()
    ciberseguridad = Facultad.query.filter_by(nombre="Facultad de Ingeniera en Ciberseguridad").first()
    electronica = Facultad.query.filter_by(nombre="Facultad de Ingeniera Electrnica").first()
    salud = Facultad.query.filter_by(nombre="Facultad de Ciencias de la Salud").first()
    empresarial = Facultad.query.filter_by(nombre="Facultad de Ciencias Empresariales").first()

    especialidades = [
        Especialidad(nombre="Ingeniera de Software", facultad_id=sistemas.id if sistemas else None),
        Especialidad(nombre="Seguridad de la Informacin", facultad_id=ciberseguridad.id if ciberseguridad else None),
        Especialidad(nombre="Ingeniera Electrnica", facultad_id=electronica.id if electronica else None),
        Especialidad(nombre="Medicina Humana", facultad_id=salud.id if salud else None),
        Especialidad(nombre="Psicologa", facultad_id=salud.id if salud else None),
        Especialidad(nombre="Administracin de Empresas", facultad_id=empresarial.id if empresarial else None),
        Especialidad(nombre="Contabilidad", facultad_id=empresarial.id if empresarial else None),
        Especialidad(nombre="Marketing", facultad_id=empresarial.id if empresarial else None),
    ]

    db.session.add_all(especialidades)
    db.session.commit()
    print("Especialidades creadas")
