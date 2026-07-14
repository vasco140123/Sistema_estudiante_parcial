from app import db
from app.modelos.docente import Docente
from app.modelos.usuario import Usuario

DOCENTES_DATA = [
    {
        "username": "docente1_prueba",
        "nombres": "Juan",
        "apellido_paterno": "Perez",
        "apellido_materno": "Gomez",
        "dni": "80000000",
        "correo": "juan.perez@universidad.edu.pe",
    },
    {
        "username": "docente2_prueba",
        "nombres": "Maria",
        "apellido_paterno": "Gomez",
        "apellido_materno": "Garcia",
        "dni": "80000001",
        "correo": "maria.gomez@universidad.edu.pe",
    },
    {
        "username": "docente3_prueba",
        "nombres": "Carlos",
        "apellido_paterno": "Garcia",
        "apellido_materno": "Torres",
        "dni": "80000002",
        "correo": "carlos.garcia@universidad.edu.pe",
    },
    {
        "username": "docente4_prueba",
        "nombres": "Ana",
        "apellido_paterno": "Torres",
        "apellido_materno": "Ruiz",
        "dni": "80000003",
        "correo": "ana.torres@universidad.edu.pe",
    },
    {
        "username": "docente5_prueba",
        "nombres": "Luis",
        "apellido_paterno": "Ruiz",
        "apellido_materno": "Flores",
        "dni": "80000004",
        "correo": "luis.ruiz@universidad.edu.pe",
    },
    {
        "username": "docente6_prueba",
        "nombres": "Elena",
        "apellido_paterno": "Flores",
        "apellido_materno": "Rojas",
        "dni": "80000005",
        "correo": "elena.flores@universidad.edu.pe",
    },
    {
        "username": "docente7_prueba",
        "nombres": "Pedro",
        "apellido_paterno": "Rojas",
        "apellido_materno": "Duran",
        "dni": "80000006",
        "correo": "pedro.rojas@universidad.edu.pe",
    },
    {
        "username": "docente8_prueba",
        "nombres": "Sofia",
        "apellido_paterno": "Duran",
        "apellido_materno": "Vargas",
        "dni": "80000007",
        "correo": "sofia.duran@universidad.edu.pe",
    },
    {
        "username": "docente9_prueba",
        "nombres": "Jorge",
        "apellido_paterno": "Vargas",
        "apellido_materno": "Rios",
        "dni": "80000008",
        "correo": "jorge.vargas@universidad.edu.pe",
    },
    {
        "username": "docente10_prueba",
        "nombres": "Lucia",
        "apellido_paterno": "Rios",
        "apellido_materno": "Perez",
        "dni": "80000009",
        "correo": "lucia.rios@universidad.edu.pe",
    },
]


def ejecutar():
    for data in DOCENTES_DATA:
        existe = Docente.query.join(Usuario).filter(Usuario.username == data["username"]).first()
        if existe: continue

        usuario = Usuario.query.filter_by(username=data["username"]).first()
        if not usuario: continue

        docente = Docente(
            usuario_id=usuario.id,
            nombres=data["nombres"],
            apellido_paterno=data["apellido_paterno"],
            apellido_materno=data["apellido_materno"],
            dni=data["dni"],
            correo_institucional=data["correo"],
        )
        db.session.add(docente)
    db.session.commit()
    print(f"Docentes creados: {Docente.query.count()}")
