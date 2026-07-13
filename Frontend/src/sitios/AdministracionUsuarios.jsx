import { useEffect, useState } from "react";
import {
  cambiarRol, listarUsuarios, crearUsuario, actualizarUsuario, eliminarUsuario,
  toggleUsuario, cambiarPassword, listarEspecialidades,
  listarPlanesEstudio, listarSemestres, crearPlanEstudio, eliminarPlanEstudio, actualizarPlanEstudio,
} from "../servicios/administracion.servicio";

const ROLES = ["estudiante", "docente", "administrador", "direccion"];

const ESTADO_INICIAL_FORM = {
  username: "", password: "", rol: "estudiante", nombres: "", apellido_paterno: "",
  apellido_materno: "", correo_institucional: "", dni: "", especialidad_id: "", plan_estudios_id: "", semestre_id: "",
};

export default function AdministracionUsuarios() {
  const [usuarios, setUsuarios] = useState([]);
  const [selecciones, setSelecciones] = useState({});
  const [mensaje, setMensaje] = useState(null);
  const [error, setError] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [busqueda, setBusqueda] = useState("");
  const [mostrarModal, setMostrarModal] = useState(false);
  const [formulario, setFormulario] = useState(ESTADO_INICIAL_FORM);
  const [creando, setCreando] = useState(false);
  const [especialidades, setEspecialidades] = useState([]);
  const [planesEstudio, setPlanesEstudio] = useState([]);
  const [semestres, setSemestres] = useState([]);
  const [modalPassword, setModalPassword] = useState(null);
  const [mostrarPlanes, setMostrarPlanes] = useState(false);
  const [nuevoPlan, setNuevoPlan] = useState({ especialidad_id: "", anio_creacion: "" });
  const [creandoPlan, setCreandoPlan] = useState(false);
  const [editandoPlan, setEditandoPlan] = useState(null);
  const [planEditForm, setPlanEditForm] = useState({ especialidad_id: "", anio_creacion: "", vigente: true });

  const [nuevaPassword, setNuevaPassword] = useState("");
  const [cambiandoPass, setCambiandoPass] = useState(false);
  const [editandoUsuario, setEditandoUsuario] = useState(null);
  const [editForm, setEditForm] = useState({});

  useEffect(() => {
    cargarUsuarios();
    listarEspecialidades().then(r => { if (r.data) setEspecialidades(r.data); });
    listarPlanesEstudio().then(r => { if (r.data) setPlanesEstudio(r.data); });
    listarSemestres().then(r => { if (r.data) setSemestres(r.data); });
  }, []);

  async function cargarUsuarios() {
    setCargando(true);
    const { data, error } = await listarUsuarios();
    setCargando(false);
    if (error) { setError(error); return; }
    setUsuarios(data);
    const inicial = {};
    data.forEach((u) => { inicial[u.id] = u.rol; });
    setSelecciones(inicial);
  }

  async function manejarCambio(usuarioId) {
    setMensaje(null); setError(null);
    const { data, error } = await cambiarRol(usuarioId, selecciones[usuarioId]);
    if (error) { setError(error); return; }
    setMensaje(data.mensaje);
    cargarUsuarios();
  }

  async function manejarToggle(usuarioId) {
    setMensaje(null); setError(null);
    const { data, error } = await toggleUsuario(usuarioId);
    if (error) { setError(error); return; }
    setMensaje(data.mensaje);
    cargarUsuarios();
  }

  function abrirModalPassword(usuario) { setModalPassword(usuario); setNuevaPassword(""); }

  async function manejarCambioPassword() {
    if (!nuevaPassword || nuevaPassword.length < 6) { setError("La contrasena debe tener al menos 6 caracteres"); return; }
    setCambiandoPass(true); setError(null);
    const { data, error } = await cambiarPassword(modalPassword.id, nuevaPassword);
    setCambiandoPass(false);
    if (error) { setError(error); return; }
    setMensaje(data.mensaje);
    setModalPassword(null); setNuevaPassword("");
  }

  async function manejarCrear(e) {
    e.preventDefault();
    setCreando(true); setError(null);
    const { data, error } = await crearUsuario(formulario);
    setCreando(false);
    if (error) { setError(error); return; }
    setMensaje(data.mensaje);
    setMostrarModal(false);
    setFormulario(ESTADO_INICIAL_FORM);
    cargarUsuarios();
  }

  function actualizarCampo(campo, valor) { setFormulario((prev) => ({ ...prev, [campo]: valor })); }

  function abrirEditar(usuario) {
    const perfil = usuario.perfil || {};
    setEditForm({
      username: usuario.username,
      rol: usuario.rol,
      nombres: perfil.nombres || "",
      apellido_paterno: perfil.apellido_paterno || "",
      apellido_materno: perfil.apellido_materno || "",
      correo_institucional: perfil.correo_institucional || "",
      dni: perfil.dni || "",
      especialidad_id: perfil.especialidad_id || "",
      plan_estudios_id: perfil.plan_estudios_id || "",
      semestre_id: perfil.semestre_id || "",
    });
    setEditandoUsuario(usuario);
  }

  function cerrarEditar() { setEditandoUsuario(null); setEditForm({}); }

  async function manejarGuardarEditar() {
    setError(null);
    const { data, error } = await actualizarUsuario(editandoUsuario.id, editForm);
    if (error) { setError(error); return; }
    setMensaje(data.mensaje);
    cerrarEditar();
    cargarUsuarios();
  }

  async function manejarEliminar(id) {
    if (!confirm("¿Eliminar este usuario? Se desactivará su cuenta.")) return;
    setError(null);
    const { data, error } = await eliminarUsuario(id);
    if (error) { setError(error); return; }
    setMensaje(data.mensaje);
    cargarUsuarios();
  }

  const necesitaPerfil = formulario.rol === "estudiante" || formulario.rol === "docente";
  const filtrados = usuarios.filter((u) =>
    u.username.toLowerCase().includes(busqueda.toLowerCase()) ||
    u.rol.toLowerCase().includes(busqueda.toLowerCase())
  );

  return (
    <div>
      <div className="flex items-start justify-between mb-8">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Usuarios y roles</h2>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setMostrarPlanes(!mostrarPlanes)}
            className="px-4 py-2 bg-white text-gray-700 text-sm font-semibold  border border-gray-300 hover:bg-gray-50 transition-colors cursor-pointer">
            {mostrarPlanes ? "Ocultar planes" : "Gestionar planes"}
          </button>
          <button onClick={() => setMostrarModal(true)}
            className="px-4 py-2 bg-primary text-white text-sm font-semibold  hover:bg-primary-hover transition-colors cursor-pointer">
            + Nuevo usuario
          </button>
        </div>
      </div>

      {mostrarPlanes && (
        <div className="bg-white  border border-gray-200 p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Planes de estudio</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6 p-4 bg-gray-50 ">
            <div>
              <label>Especialidad</label>
              <select value={nuevoPlan.especialidad_id} onChange={(e) => setNuevoPlan({ ...nuevoPlan, especialidad_id: e.target.value })}>
                <option value="">Seleccionar...</option>
                {especialidades.map((esp) => (<option key={esp.id} value={esp.id}>{esp.nombre}</option>))}
              </select>
            </div>
            <div>
              <label>Año de creación</label>
              <input type="number" value={nuevoPlan.anio_creacion} onChange={(e) => setNuevoPlan({ ...nuevoPlan, anio_creacion: e.target.value })} placeholder="Ej: 2024" />
            </div>
            <div className="flex items-end">
              <button onClick={async () => {
                if (!nuevoPlan.especialidad_id || !nuevoPlan.anio_creacion) { setError("Completa todos los campos"); return; }
                setCreandoPlan(true);
                const { data, error } = await crearPlanEstudio({ especialidad_id: Number(nuevoPlan.especialidad_id), anio_creacion: Number(nuevoPlan.anio_creacion) });
                setCreandoPlan(false);
                if (error) { setError(error); return; }
                setMensaje(data.mensaje);
                setNuevoPlan({ especialidad_id: "", anio_creacion: "" });
                listarPlanesEstudio().then(r => { if (r.data) setPlanesEstudio(r.data); });
              }} disabled={creandoPlan}
                className="px-4 py-2 bg-primary text-white text-sm font-semibold  hover:bg-primary-hover disabled:bg-gray-300 disabled:text-gray-500 transition-colors cursor-pointer">
                {creandoPlan ? "Creando..." : "Crear plan"}
              </button>
            </div>
          </div>

          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">ID</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Nombre</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Especialidad</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Vigente</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {planesEstudio.length === 0 ? (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-sm text-gray-500">No hay planes de estudio registrados.</td></tr>
              ) : planesEstudio.map((p) => (
                <tr key={p.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-900 font-medium">{p.id}</td>
                  <td className="px-4 py-3 text-gray-600">{p.nombre || `Plan ${p.anio_creacion}`}</td>
                  <td className="px-4 py-3 text-gray-600">{p.especialidad_nombre || p.especialidad_id}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center px-2.5 py-0.5  text-xs font-medium border ${p.vigente ? "bg-green-50 text-green-700 border-green-200" : "bg-red-50 text-red-700 border-red-200"}`}>
                      {p.vigente ? "Si" : "No"}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-1.5">
                      <button onClick={() => { setEditandoPlan(p.id); setPlanEditForm({ especialidad_id: p.especialidad_id, anio_creacion: p.anio_creacion, vigente: p.vigente }); }}
                        className="px-2.5 py-1 text-xs font-semibold  border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 transition-colors cursor-pointer">
                        Editar
                      </button>
                      <button onClick={async () => {
                        if (!confirm("¿Eliminar este plan de estudios?")) return;
                        const { data, error } = await eliminarPlanEstudio(p.id);
                        if (error) { setError(error); return; }
                        setMensaje(data.mensaje);
                        listarPlanesEstudio().then(r => { if (r.data) setPlanesEstudio(r.data); });
                      }}
                        className="px-2.5 py-1 text-xs font-semibold  bg-red-50 text-red-700 border border-red-200 hover:bg-red-100 transition-colors cursor-pointer">
                        Eliminar
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {editandoPlan && (
                <tr className="bg-blue-50">
                  <td colSpan={5} className="px-4 py-3">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-3 items-end">
                      <div>
                        <label className="text-xs">Especialidad</label>
                        <select value={planEditForm.especialidad_id} onChange={(e) => setPlanEditForm({ ...planEditForm, especialidad_id: Number(e.target.value) })}>
                          {especialidades.map((esp) => (<option key={esp.id} value={esp.id}>{esp.nombre}</option>))}
                        </select>
                      </div>
                      <div>
                        <label className="text-xs">Año</label>
                        <input type="number" value={planEditForm.anio_creacion} onChange={(e) => setPlanEditForm({ ...planEditForm, anio_creacion: Number(e.target.value) })} />
                      </div>
                      <div>
                        <label className="text-xs">Vigente</label>
                        <select value={planEditForm.vigente} onChange={(e) => setPlanEditForm({ ...planEditForm, vigente: e.target.value === "true" })}>
                          <option value="true">Si</option>
                          <option value="false">No</option>
                        </select>
                      </div>
                      <div className="flex gap-2">
                        <button onClick={async () => {
                          const { data, error } = await actualizarPlanEstudio(editandoPlan, planEditForm);
                          if (error) { setError(error); return; }
                          setMensaje(data.mensaje);
                          setEditandoPlan(null);
                          listarPlanesEstudio().then(r => { if (r.data) setPlanesEstudio(r.data); });
                        }}
                          className="px-3 py-1.5 text-xs font-semibold  bg-primary text-white hover:bg-primary-hover transition-colors cursor-pointer">
                          Guardar
                        </button>
                        <button onClick={() => setEditandoPlan(null)}
                          className="px-3 py-1.5 text-xs font-semibold  border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 transition-colors cursor-pointer">
                          Cancelar
                        </button>
                      </div>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {mensaje && <div className="mb-6 p-3 bg-green-50 border border-green-200 text-green-700 text-sm ">{mensaje}</div>}
      {error && <div className="mb-6 p-3 bg-red-50 border border-red-200 text-red-700 text-sm ">{error}</div>}

      <div className="bg-white  border border-gray-200 overflow-hidden mb-8">
        <div className="p-4 border-b border-gray-200">
          <input type="text" placeholder="Buscar por usuario o rol..." value={busqueda} onChange={(e) => setBusqueda(e.target.value)} />
        </div>

        {cargando && <p className="text-sm text-gray-500 p-4">Cargando usuarios...</p>}

        {!cargando && filtrados.length === 0 && (
          <p className="text-sm text-gray-500 text-center py-8">{busqueda ? "No se encontraron usuarios con ese criterio." : "No hay usuarios registrados."}</p>
        )}

        {!cargando && filtrados.length > 0 && (
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">ID</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Usuario</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Estado</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Rol actual</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Cambiar rol</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Plan</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filtrados.map((usuario) => (
                <tr key={usuario.id} className={`hover:bg-gray-50 ${!usuario.activo ? "opacity-50" : ""}`}>
                  <td className="px-4 py-3 text-gray-900 font-medium">{usuario.id}</td>
                  <td className="px-4 py-3">
                    <span className="text-gray-900">{usuario.username}</span>
                    {usuario.perfil && (
                      <span className="text-xs text-gray-400 block">{usuario.perfil.nombres} {usuario.perfil.apellido_paterno}</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center px-2.5 py-0.5  text-xs font-medium border ${
                      usuario.activo ? "bg-green-50 text-green-700 border-green-200" : "bg-red-50 text-red-700 border-red-200"
                    }`}>{usuario.activo ? "Activo" : "Inactivo"}</span>
                  </td>
                  <td className="px-4 py-3 text-gray-600">{usuario.rol}</td>
                  <td className="px-4 py-3">
                    <select value={selecciones[usuario.id] || usuario.rol}
                      onChange={(e) => setSelecciones((prev) => ({ ...prev, [usuario.id]: e.target.value }))}>
                      {ROLES.map((rol) => (<option key={rol} value={rol}>{rol}</option>))}
                    </select>
                  </td>
                  <td className="px-4 py-3">
                    {usuario.rol === "estudiante" ? (
                      <span className="text-xs text-gray-600">
                        {usuario.perfil?.plan_estudios_nombre || (
                          <span className="text-yellow-600 font-medium">Sin plan</span>
                        )}
                      </span>
                    ) : (
                      <span className="text-xs text-gray-400">—</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-1.5 flex-wrap">
                      <button onClick={() => manejarCambio(usuario.id)}
                        className="px-2.5 py-1 text-xs font-semibold  bg-primary text-white hover:bg-primary-hover transition-colors cursor-pointer">
                        Cambiar rol
                      </button>
                      <button onClick={() => manejarToggle(usuario.id)}
                        className="px-2.5 py-1 text-xs font-semibold  border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 transition-colors cursor-pointer">
                        {usuario.activo ? "Desactivar" : "Activar"}
                      </button>
                      <button onClick={() => abrirModalPassword(usuario)}
                        className="px-2.5 py-1 text-xs font-semibold  border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 transition-colors cursor-pointer">
                        Password
                      </button>
                      <button onClick={() => abrirEditar(usuario)}
                        className="px-2.5 py-1 text-xs font-semibold  border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 transition-colors cursor-pointer">
                        Editar
                      </button>
                      <button onClick={() => manejarEliminar(usuario.id)}
                        className="px-2.5 py-1 text-xs font-semibold  bg-red-50 text-red-700 border border-red-200 hover:bg-red-100 transition-colors cursor-pointer">
                        Eliminar
                      </button>

                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {mostrarModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center" onClick={() => setMostrarModal(false)}>
          <div className="bg-white  shadow-xl p-6 w-full max-w-lg mx-4" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold text-gray-900 mb-4">Nuevo usuario</h3>
            <form onSubmit={manejarCrear}>
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <label>Usuario *</label>
                  <input type="text" required value={formulario.username} onChange={(e) => actualizarCampo("username", e.target.value)} />
                </div>
                <div>
                  <label>Contrasena *</label>
                  <input type="password" required minLength={6} value={formulario.password} onChange={(e) => actualizarCampo("password", e.target.value)} />
                </div>
              </div>
              <div className="mb-4">
                <label>Rol *</label>
                <select value={formulario.rol} onChange={(e) => actualizarCampo("rol", e.target.value)}>
                  {ROLES.map((rol) => (<option key={rol} value={rol}>{rol}</option>))}
                </select>
              </div>
              {necesitaPerfil && (
                <>
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <label>Nombres *</label>
                      <input type="text" required value={formulario.nombres} onChange={(e) => actualizarCampo("nombres", e.target.value)} />
                    </div>
                    <div>
                      <label>Apellido paterno *</label>
                      <input type="text" required value={formulario.apellido_paterno} onChange={(e) => actualizarCampo("apellido_paterno", e.target.value)} />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <label>Apellido materno *</label>
                      <input type="text" required value={formulario.apellido_materno} onChange={(e) => actualizarCampo("apellido_materno", e.target.value)} />
                    </div>
                    <div>
                      <label>Correo institucional *</label>
                      <input type="email" required value={formulario.correo_institucional} onChange={(e) => actualizarCampo("correo_institucional", e.target.value)} />
                    </div>
                    <div>
                      <label>DNI *</label>
                      <input type="text" required maxLength={8} minLength={8} value={formulario.dni} onChange={(e) => actualizarCampo("dni", e.target.value)} placeholder="8 dígitos" />
                    </div>
                  </div>
                  {formulario.rol === "estudiante" && (
                    <>
                      <div className="mb-4">
                        <label>Especialidad *</label>
                        <select required value={formulario.especialidad_id} onChange={(e) => actualizarCampo("especialidad_id", e.target.value)}>
                          <option value="">Seleccionar...</option>
                          {especialidades.map((esp) => (<option key={esp.id} value={esp.id}>{esp.nombre}</option>))}
                        </select>
                      </div>
                      <div className="mb-4">
                        <label>Plan de estudios</label>
                        <select value={formulario.plan_estudios_id} onChange={(e) => { actualizarCampo("plan_estudios_id", e.target.value); actualizarCampo("semestre_id", ""); }}>
                          <option value="">Sin plan</option>
                          {planesEstudio.map((p) => (
                            <option key={p.id} value={p.id}>{p.nombre || `Plan ${p.anio_creacion}`}</option>
                          ))}
                        </select>
                      </div>
                      {formulario.plan_estudios_id && (
                        <div className="mb-4">
                          <label>Semestre *</label>
                          <select required value={formulario.semestre_id} onChange={(e) => actualizarCampo("semestre_id", e.target.value)}>
                            <option value="">Seleccionar...</option>
                            {semestres.map((s) => (
                              <option key={s.id} value={s.id}>{s.codigo}</option>
                            ))}
                          </select>
                        </div>
                      )}
                    </>
                  )}
                </>
              )}
              <div className="flex gap-3 justify-end mt-6">
                <button type="button" onClick={() => setMostrarModal(false)}
                  className="px-4 py-2 text-sm font-semibold  border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 transition-colors cursor-pointer">
                  Cancelar
                </button>
                <button type="submit" disabled={creando}
                  className="px-4 py-2 text-sm font-semibold  bg-primary text-white hover:bg-primary-hover disabled:bg-gray-300 disabled:text-gray-500 transition-colors cursor-pointer">
                  {creando ? "Creando..." : "Crear usuario"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {editandoUsuario && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center" onClick={cerrarEditar}>
          <div className="bg-white  shadow-xl p-6 w-full max-w-lg mx-4" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold text-gray-900 mb-4">Editar usuario</h3>
            <p className="text-sm text-gray-500 mb-4">Usuario: <strong>{editandoUsuario.username}</strong> ({editandoUsuario.rol})</p>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="col-span-2">
                <label>Username</label>
                <input type="text" value={editForm.username} onChange={(e) => setEditForm({ ...editForm, username: e.target.value })} />
              </div>
            </div>
            {(editandoUsuario.rol === "estudiante" || editandoUsuario.rol === "docente") && (
              <>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <label>Nombres</label>
                    <input type="text" value={editForm.nombres} onChange={(e) => setEditForm({ ...editForm, nombres: e.target.value })} />
                  </div>
                  <div>
                    <label>Apellido paterno</label>
                    <input type="text" value={editForm.apellido_paterno} onChange={(e) => setEditForm({ ...editForm, apellido_paterno: e.target.value })} />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <label>Apellido materno</label>
                    <input type="text" value={editForm.apellido_materno} onChange={(e) => setEditForm({ ...editForm, apellido_materno: e.target.value })} />
                  </div>
                  <div>
                    <label>Correo</label>
                    <input type="email" value={editForm.correo_institucional} onChange={(e) => setEditForm({ ...editForm, correo_institucional: e.target.value })} />
                  </div>
                </div>
              </>
            )}
            {editandoUsuario.rol === "estudiante" && (
              <>
                <div className="mb-4">
                  <label>Especialidad</label>
                  <select value={editForm.especialidad_id} onChange={(e) => setEditForm({ ...editForm, especialidad_id: e.target.value })}>
                    <option value="">Seleccionar...</option>
                    {especialidades.map((esp) => (<option key={esp.id} value={esp.id}>{esp.nombre}</option>))}
                  </select>
                </div>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <label>Plan de estudios</label>
                    <select value={editForm.plan_estudios_id} onChange={(e) => setEditForm({ ...editForm, plan_estudios_id: e.target.value, semestre_id: "" })}>
                      <option value="">Sin plan</option>
                      {planesEstudio.map((p) => (
                        <option key={p.id} value={p.id}>{p.nombre || `Plan ${p.anio_creacion}`}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label>Semestre</label>
                    <select value={editForm.semestre_id} onChange={(e) => setEditForm({ ...editForm, semestre_id: e.target.value })}>
                      <option value="">Seleccionar...</option>
                      {semestres.map((s) => (<option key={s.id} value={s.id}>{s.codigo}</option>))}
                    </select>
                  </div>
                </div>
              </>
            )}
            <div className="flex gap-3 justify-end mt-6">
              <button onClick={cerrarEditar}
                className="px-4 py-2 text-sm font-semibold  border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 transition-colors cursor-pointer">
                Cancelar
              </button>
              <button onClick={manejarGuardarEditar}
                className="px-4 py-2 text-sm font-semibold  bg-primary text-white hover:bg-primary-hover transition-colors cursor-pointer">
                Guardar cambios
              </button>
            </div>
          </div>
        </div>
      )}

      {modalPassword && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center" onClick={() => setModalPassword(null)}>
          <div className="bg-white  shadow-xl p-6 w-full max-w-sm mx-4" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold text-gray-900 mb-2">Cambiar contrasena</h3>
            <p className="text-sm text-gray-500 mb-4">Usuario: <strong>{modalPassword.username}</strong></p>
            <div className="mb-4">
              <label>Nueva contrasena</label>
              <input type="password" minLength={6} value={nuevaPassword} onChange={(e) => setNuevaPassword(e.target.value)} placeholder="Minimo 6 caracteres" />
            </div>
            <div className="flex gap-3 justify-end">
              <button onClick={() => setModalPassword(null)}
                className="px-4 py-2 text-sm font-semibold  border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 transition-colors cursor-pointer">
                Cancelar
              </button>
              <button onClick={manejarCambioPassword} disabled={cambiandoPass}
                className="px-4 py-2 text-sm font-semibold  bg-primary text-white hover:bg-primary-hover disabled:bg-gray-300 disabled:text-gray-500 transition-colors cursor-pointer">
                {cambiandoPass ? "Cambiando..." : "Cambiar contrasena"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
