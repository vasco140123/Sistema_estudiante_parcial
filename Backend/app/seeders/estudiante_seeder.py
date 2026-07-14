from app import db
from app.modelos.especialidad import Especialidad
from app.modelos.estudiante import Estudiante
from app.modelos.usuario import Usuario

ESTUDIANTES_DATA = [
    {
        "username": "estudiante1_prueba",
        "nombres": "Andres",
        "apellido_paterno": "Silva",
        "apellido_materno": "Reyes",
        "dni": "70000000",
        "correo": "andres@universidad.edu.pe",
    },
    {
        "username": "estudiante2_prueba",
        "nombres": "Camila",
        "apellido_paterno": "Mendoza",
        "apellido_materno": "Aguilar",
        "dni": "70000001",
        "correo": "camila@universidad.edu.pe",
    },
    {
        "username": "estudiante3_prueba",
        "nombres": "Diego",
        "apellido_paterno": "Castillo",
        "apellido_materno": "Ortiz",
        "dni": "70000002",
        "correo": "diego@universidad.edu.pe",
    },
    {
        "username": "estudiante4_prueba",
        "nombres": "Valentina",
        "apellido_paterno": "Reyes",
        "apellido_materno": "Morales",
        "dni": "70000003",
        "correo": "valentina@universidad.edu.pe",
    },
    {
        "username": "estudiante5_prueba",
        "nombres": "Mateo",
        "apellido_paterno": "Aguilar",
        "apellido_materno": "Cruz",
        "dni": "70000004",
        "correo": "mateo@universidad.edu.pe",
    },
    {
        "username": "estudiante6_prueba",
        "nombres": "Renata",
        "apellido_paterno": "Ortiz",
        "apellido_materno": "Ramos",
        "dni": "70000005",
        "correo": "renata@universidad.edu.pe",
    },
    {
        "username": "estudiante7_prueba",
        "nombres": "Sebastian",
        "apellido_paterno": "Morales",
        "apellido_materno": "Herrera",
        "dni": "70000006",
        "correo": "sebastian@universidad.edu.pe",
    },
    {
        "username": "estudiante8_prueba",
        "nombres": "Valeria",
        "apellido_paterno": "Cruz",
        "apellido_materno": "Silva",
        "dni": "70000007",
        "correo": "valeria@universidad.edu.pe",
    },
    {
        "username": "estudiante9_prueba",
        "nombres": "Alejandro",
        "apellido_paterno": "Ramos",
        "apellido_materno": "Mendoza",
        "dni": "70000008",
        "correo": "alejandro@universidad.edu.pe",
    },
    {
        "username": "estudiante10_prueba",
        "nombres": "Daniela",
        "apellido_paterno": "Herrera",
        "apellido_materno": "Castillo",
        "dni": "70000009",
        "correo": "daniela@universidad.edu.pe",
    },
    {
        "username": "estudiante11_prueba",
        "nombres": "Fernando",
        "apellido_paterno": "Silva",
        "apellido_materno": "Reyes",
        "dni": "70000010",
        "correo": "fernando@universidad.edu.pe",
    },
    {
        "username": "estudiante12_prueba",
        "nombres": "Mariana",
        "apellido_paterno": "Mendoza",
        "apellido_materno": "Aguilar",
        "dni": "70000011",
        "correo": "mariana@universidad.edu.pe",
    },
    {
        "username": "estudiante13_prueba",
        "nombres": "Joaquin",
        "apellido_paterno": "Castillo",
        "apellido_materno": "Ortiz",
        "dni": "70000012",
        "correo": "joaquin@universidad.edu.pe",
    },
    {
        "username": "estudiante14_prueba",
        "nombres": "Victoria",
        "apellido_paterno": "Reyes",
        "apellido_materno": "Morales",
        "dni": "70000013",
        "correo": "victoria@universidad.edu.pe",
    },
    {
        "username": "estudiante15_prueba",
        "nombres": "Emilio",
        "apellido_paterno": "Aguilar",
        "apellido_materno": "Cruz",
        "dni": "70000014",
        "correo": "emilio@universidad.edu.pe",
    },
    {
        "username": "estudiante16_prueba",
        "nombres": "Isabella",
        "apellido_paterno": "Ortiz",
        "apellido_materno": "Ramos",
        "dni": "70000015",
        "correo": "isabella@universidad.edu.pe",
    },
    {
        "username": "estudiante17_prueba",
        "nombres": "Rodrigo",
        "apellido_paterno": "Morales",
        "apellido_materno": "Herrera",
        "dni": "70000016",
        "correo": "rodrigo@universidad.edu.pe",
    },
    {
        "username": "estudiante18_prueba",
        "nombres": "Ximena",
        "apellido_paterno": "Cruz",
        "apellido_materno": "Silva",
        "dni": "70000017",
        "correo": "ximena@universidad.edu.pe",
    },
    {
        "username": "estudiante19_prueba",
        "nombres": "Hugo",
        "apellido_paterno": "Ramos",
        "apellido_materno": "Mendoza",
        "dni": "70000018",
        "correo": "hugo@universidad.edu.pe",
    },
    {
        "username": "estudiante20_prueba",
        "nombres": "Andrea",
        "apellido_paterno": "Herrera",
        "apellido_materno": "Castillo",
        "dni": "70000019",
        "correo": "andrea@universidad.edu.pe",
    },
    {
        "username": "estudiante21_prueba",
        "nombres": "Gabriel",
        "apellido_paterno": "Silva",
        "apellido_materno": "Reyes",
        "dni": "70000020",
        "correo": "gabriel@universidad.edu.pe",
    },
    {
        "username": "estudiante22_prueba",
        "nombres": "Natalia",
        "apellido_paterno": "Mendoza",
        "apellido_materno": "Aguilar",
        "dni": "70000021",
        "correo": "natalia@universidad.edu.pe",
    },
    {
        "username": "estudiante23_prueba",
        "nombres": "Nicolas",
        "apellido_paterno": "Castillo",
        "apellido_materno": "Ortiz",
        "dni": "70000022",
        "correo": "nicolas@universidad.edu.pe",
    },
    {
        "username": "estudiante24_prueba",
        "nombres": "Paula",
        "apellido_paterno": "Reyes",
        "apellido_materno": "Morales",
        "dni": "70000023",
        "correo": "paula@universidad.edu.pe",
    },
    {
        "username": "estudiante25_prueba",
        "nombres": "Samuel",
        "apellido_paterno": "Aguilar",
        "apellido_materno": "Cruz",
        "dni": "70000024",
        "correo": "samuel@universidad.edu.pe",
    },
    {
        "username": "estudiante26_prueba",
        "nombres": "Fernanda",
        "apellido_paterno": "Ortiz",
        "apellido_materno": "Ramos",
        "dni": "70000025",
        "correo": "fernanda@universidad.edu.pe",
    },
    {
        "username": "estudiante27_prueba",
        "nombres": "Matias",
        "apellido_paterno": "Morales",
        "apellido_materno": "Herrera",
        "dni": "70000026",
        "correo": "matias@universidad.edu.pe",
    },
    {
        "username": "estudiante28_prueba",
        "nombres": "Romina",
        "apellido_paterno": "Cruz",
        "apellido_materno": "Silva",
        "dni": "70000027",
        "correo": "romina@universidad.edu.pe",
    },
    {
        "username": "estudiante29_prueba",
        "nombres": "Tomas",
        "apellido_paterno": "Ramos",
        "apellido_materno": "Mendoza",
        "dni": "70000028",
        "correo": "tomas@universidad.edu.pe",
    },
    {
        "username": "estudiante30_prueba",
        "nombres": "Julieta",
        "apellido_paterno": "Herrera",
        "apellido_materno": "Castillo",
        "dni": "70000029",
        "correo": "julieta@universidad.edu.pe",
    },
]


def ejecutar():
    especialidades = Especialidad.query.all()
    if not especialidades: return

    for i, data in enumerate(ESTUDIANTES_DATA):
        existe = Estudiante.query.join(Usuario).filter(Usuario.username == data["username"]).first()
        if existe: continue

        usuario = Usuario.query.filter_by(username=data["username"]).first()
        if not usuario: continue

        # Asignar especialidades rotativas
        especialidad = especialidades[i % len(especialidades)]

        estudiante = Estudiante(
            usuario_id=usuario.id,
            especialidad_id=especialidad.id,
            nombres=data["nombres"],
            apellido_paterno=data["apellido_paterno"],
            apellido_materno=data["apellido_materno"],
            dni=data["dni"],
            correo_institucional=data["correo"],
            tiene_deuda_activa=False,
            tiene_sancion_activa=False,
        )
        db.session.add(estudiante)
    db.session.commit()
    print(f"Estudiantes creados: {Estudiante.query.count()}")
