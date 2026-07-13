from flask import Blueprint, jsonify
from app.modulos.administracion import controllers
from app.utils.middlewares import rol_requerido

administracion_bp = Blueprint('administracion', __name__)


@administracion_bp.route('/', methods=['GET'])
def index_administracion():
    return jsonify({
        "endpoints": [
            "/facultades",
            "/especialidades",
            "/planes-estudio",
            "/semestres",
            "/usuarios",
            "/usuarios/<id>/rol",
            "/auditorias"
        ]
    })


@administracion_bp.route('/facultades', methods=['GET'])
def listar_facultades():
    return controllers.listar_facultades()


@administracion_bp.route('/especialidades', methods=['GET'])
def listar_especialidades():
    return controllers.listar_especialidades()


@administracion_bp.route('/planes-estudio', methods=['GET'])
def listar_planes_estudio():
    return controllers.listar_planes_estudio()


@administracion_bp.route('/planes-estudio', methods=['POST'])
@rol_requerido("administrador")
def crear_plan_estudio():
    return controllers.crear_plan_estudio()


@administracion_bp.route('/planes-estudio/<int:plan_id>', methods=['PUT'])
@rol_requerido("administrador")
def actualizar_plan_estudio(plan_id):
    return controllers.actualizar_plan_estudio(plan_id)


@administracion_bp.route('/planes-estudio/<int:plan_id>', methods=['DELETE'])
@rol_requerido("administrador")
def eliminar_plan_estudio(plan_id):
    return controllers.eliminar_plan_estudio(plan_id)


@administracion_bp.route('/semestres', methods=['GET'])
def listar_semestres():
    return controllers.listar_semestres()


@administracion_bp.route('/periodos', methods=['GET'])
def listar_periodos():
    return controllers.listar_periodos()


@administracion_bp.route('/usuarios', methods=['GET'])
@rol_requerido("administrador")
def listar_usuarios():
    return controllers.listar_usuarios()


@administracion_bp.route('/usuarios/<int:usuario_id>/rol', methods=['PUT'])
@rol_requerido("administrador")
def cambiar_rol(usuario_id):
    return controllers.cambiar_rol(usuario_id)


@administracion_bp.route('/usuarios/<int:usuario_id>/toggle', methods=['POST'])
@rol_requerido("administrador")
def toggle_usuario(usuario_id):
    return controllers.toggle_usuario(usuario_id)


@administracion_bp.route('/usuarios/<int:usuario_id>/password', methods=['PUT'])
@rol_requerido("administrador")
def cambiar_password(usuario_id):
    return controllers.cambiar_password(usuario_id)


@administracion_bp.route('/usuarios/<int:usuario_id>', methods=['GET'])
@rol_requerido("administrador")
def detalle_usuario(usuario_id):
    return controllers.detalle_usuario(usuario_id)


@administracion_bp.route('/usuarios/crear', methods=['POST'])
@rol_requerido("administrador")
def crear_usuario():
    return controllers.crear_usuario()


@administracion_bp.route('/docentes', methods=['POST'])
@rol_requerido("administrador")
def registrar_docente():
    return controllers.registrar_docente()


@administracion_bp.route('/usuarios/<int:usuario_id>', methods=['PUT'])
@rol_requerido("administrador")
def actualizar_usuario(usuario_id):
    return controllers.actualizar_usuario(usuario_id)


@administracion_bp.route('/usuarios/<int:usuario_id>', methods=['DELETE'])
@rol_requerido("administrador")
def eliminar_usuario(usuario_id):
    return controllers.eliminar_usuario(usuario_id)


@administracion_bp.route('/estudiantes/<int:estudiante_id>/plan', methods=['PUT'])
@rol_requerido("administrador", "direccion")
def asignar_plan_estudiante(estudiante_id):
    return controllers.asignar_plan_estudiante(estudiante_id)


@administracion_bp.route('/planes-estudio/<int:plan_id>/cursos', methods=['GET'])
@rol_requerido("administrador", "direccion")
def listar_cursos_plan(plan_id):
    return controllers.listar_cursos_plan(plan_id)


@administracion_bp.route('/planes-estudio/<int:plan_id>/cursos', methods=['POST'])
@rol_requerido("administrador")
def asignar_curso_plan(plan_id):
    return controllers.asignar_curso_plan(plan_id)


@administracion_bp.route('/planes-estudio/cursos/<int:pcs_id>', methods=['DELETE'])
@rol_requerido("administrador")
def eliminar_curso_plan(pcs_id):
    return controllers.eliminar_curso_plan(pcs_id)


@administracion_bp.route('/auditorias', methods=['GET'])
@rol_requerido("direccion")
def listar_auditorias():
    return controllers.listar_auditorias()

@administracion_bp.route('/reportes-estrategicos', methods=['GET'])
@rol_requerido("direccion")
def reportes_estrategicos():
    return controllers.reportes_estrategicos()


admin_bp = Blueprint('admin_ciclo_global', __name__)


@admin_bp.route('/configuracion/ciclo-global', methods=['GET'])
@rol_requerido("administrador")
def configuracion_ciclo_global():
    return controllers.obtener_configuracion_ciclo()


@admin_bp.route('/configuracion/ciclo-global', methods=['PUT'])
@rol_requerido("administrador")
def actualizar_configuracion_ciclo_global():
    return controllers.actualizar_configuracion_ciclo()