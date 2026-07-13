from sqlalchemy import text
from app import crear_app, db
from app.seeders import ejecutar_todos

app = crear_app()

with app.app_context():
    respuesta = input("Esto va a borrar TODA la base de datos y recrearla. ¿Continuar? (si/no): ")

    if respuesta.lower() != "si":
        print("Operación cancelada")
        exit()

    es_mysql = db.engine.dialect.name == "mysql"

    if es_mysql:
        with db.engine.connect() as conexion:
            conexion.execute(text("SET FOREIGN_KEY_CHECKS=0"))
            conexion.commit()

    db.drop_all()
    db.create_all()

    if es_mysql:
        with db.engine.connect() as conexion:
            conexion.execute(text("SET FOREIGN_KEY_CHECKS=1"))
            conexion.commit()

    print("Base de datos recreada desde modelos")

    ejecutar_todos()

    print("")
    print("=" * 50)
    print("BASE DE DATOS INICIALIZADA")
    print("=" * 50)
    print("")
    print("Usuarios de prueba (contraseña: 123456):")
    print("  admin_prueba      -> administrador")
    print("  direccion_prueba  -> direccion")
    print("  docente1_prueba   -> docente")
    print("  estudiante1_prueba -> estudiante")
    print("")
    print("Credenciales login: username + password")
