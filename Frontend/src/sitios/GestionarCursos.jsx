import { useEffect, useState } from "react";
import {
  listarCursos, crearCurso, actualizarCurso, eliminarCurso,
} from "../servicios/cursos.servicio";
import {
  listarPlanesEstudio, listarSemestres, listarEspecialidades,
} from "../servicios/administracion.servicio";
import {
  listarCursosPlan, asignarCursoPlan, eliminarCursoPlan,
} from "../servicios/cursos.servicio";
import {
  listarPrerequisitos, crearPrerequisito, eliminarPrerequisito,
} from "../servicios/cursosDocentes.servicio";

const CURSO_VACIO = { nombre: "", codigo: "", creditos: "", horas_lectivas: "", horas_practicas: "" };

export default function GestionarCursos() {
  const [cursos, setCursos] = useState([]);
  const [planes, setPlanes] = useState([]);
  const [semestres, setSemestres] = useState([]);
  const [especialidades, setEspecialidades] = useState([]);
  const [mensaje, setMensaje] = useState(null);
  const [error, setError] = useState(null);
  const [cargando, setCargando] = useState(true);

  const [mostrarModalCurso, setMostrarModalCurso] = useState(false);
  const [cursoForm, setCursoForm] = useState(CURSO_VACIO);
  const [editandoCurso, setEditandoCurso] = useState(null);
  const [guardando, setGuardando] = useState(false);

  const [planSeleccionado, setPlanSeleccionado] = useState("");
  const [cursosPlan, setCursosPlan] = useState([]);
  const [modalAsignar, setModalAsignar] = useState(false);
  const [asignarForm, setAsignarForm] = useState({ semestre_id: "", curso_id: "" });
  const [asignando, setAsignando] = useState(false);

  const [prerequisitos, setPrerequisitos] = useState([]);
  const [cursoPreReq, setCursoPreReq] = useState("");
  const [cursoReqSeleccionado, setCursoReqSeleccionado] = useState("");
  const [agregandoPreReq, setAgregandoPreReq] = useState(false);

  useEffect(() => {
    cargarCursos();
    listarPlanesEstudio().then(r => { if (r.data) setPlanes(r.data); });
    listarSemestres().then(r => { if (r.data) setSemestres(r.data); });
    listarEspecialidades().then(r => { if (r.data) setEspecialidades(r.data); });
    cargarPrerequisitos();
  }, []);

  useEffect(() => {
    if (planSeleccionado) {
      listarCursosPlan(planSeleccionado).then(r => {
        if (r.data) setCursosPlan(r.data);
      });
    } else {
      setCursosPlan([]);
    }
  }, [planSeleccionado]);

  async function cargarCursos() {
    setCargando(true);
    const { data, error } = await listarCursos();
    setCargando(false);
    if (error) { setError(error); return; }
    setCursos(data || []);
  }

  function abrirNuevoCurso() {
    setEditandoCurso(null);
    setCursoForm(CURSO_VACIO);
    setMostrarModalCurso(true);
  }

  function abrirEditarCurso(curso) {
    setEditandoCurso(curso.id);
    setCursoForm({
      nombre: curso.nombre,
      codigo: curso.codigo,
      creditos: curso.creditos,
      horas_lectivas: curso.horas_lectivas,
      horas_practicas: curso.horas_practicas,
    });
    setMostrarModalCurso(true);
  }

  async function guardarCurso(e) {
    e.preventDefault();
    setGuardando(true);
    setError(null);
    const payload = {
      ...cursoForm,
      creditos: Number(cursoForm.creditos),
      horas_lectivas: Number(cursoForm.horas_lectivas),
      horas_practicas: Number(cursoForm.horas_practicas),
    };
    const fn = editandoCurso ? actualizarCurso(editandoCurso, payload) : crearCurso(payload);
    const { data, error } = await fn;
    setGuardando(false);
    if (error) { setError(error); return; }
    setMensaje(data.mensaje);
    setMostrarModalCurso(false);
    cargarCursos();
  }

  async function manejarEliminarCurso(id) {
    if (!confirm("¿Eliminar este curso?")) return;
    const { data, error } = await eliminarCurso(id);
    if (error) { setError(error); return; }
    setMensaje(data.mensaje);
    cargarCursos();
  }

  async function manejarAsignarCurso() {
    if (!asignarForm.semestre_id || !asignarForm.curso_id) return;
    setAsignando(true);
    setError(null);
    const { data, error } = await asignarCursoPlan(planSeleccionado, {
      semestre_id: Number(asignarForm.semestre_id),
      curso_id: Number(asignarForm.curso_id),
    });
    setAsignando(false);
    if (error) { setError(error); return; }
    setMensaje(data.mensaje);
    setModalAsignar(false);
    setAsignarForm({ semestre_id: "", curso_id: "" });
    listarCursosPlan(planSeleccionado).then(r => { if (r.data) setCursosPlan(r.data); });
  }

  async function manejarEliminarCursoPlan(pcsId) {
    if (!confirm("¿Quitar este curso del plan?")) return;
    const { data, error } = await eliminarCursoPlan(pcsId);
    if (error) { setError(error); return; }
    setMensaje(data.mensaje);
    listarCursosPlan(planSeleccionado).then(r => { if (r.data) setCursosPlan(r.data); });
  }

  const cursosNoAsignados = cursos.filter(c => !cursosPlan.some(cp => cp.curso_id === c.id));

  async function cargarPrerequisitos() {
    const { data } = await listarPrerequisitos();
    if (data) setPrerequisitos(data);
  }

  async function agregarPrerequisito() {
    if (!cursoPreReq || !cursoReqSeleccionado) return;
    setAgregandoPreReq(true);
    const { error } = await crearPrerequisito(Number(cursoPreReq), Number(cursoReqSeleccionado));
    setAgregandoPreReq(false);
    if (error) { setError(error); return; }
    setMensaje("Prerequisito agregado");
    setCursoPreReq("");
    setCursoReqSeleccionado("");
    cargarPrerequisitos();
  }

  async function eliminarPrerequisitoHandler(dependienteId, requisitoId) {
    const { error } = await eliminarPrerequisito(dependienteId, requisitoId);
    if (error) { setError(error); return; }
    setMensaje("Prerequisito eliminado");
    cargarPrerequisitos();
  }

  function nombreCurso(id) {
    const c = cursos.find(c => c.id === id);
    return c ? `${c.nombre} (${c.codigo})` : `Curso #${id}`;
  }

  const prerequisitosPorCurso = {};
  prerequisitos.forEach(p => {
    if (!prerequisitosPorCurso[p.curso_dependiente_id]) {
      prerequisitosPorCurso[p.curso_dependiente_id] = [];
    }
    prerequisitosPorCurso[p.curso_dependiente_id].push(p.curso_requisito_id);
  });

  const cursosConPrerequisitos = Object.keys(prerequisitosPorCurso).map(Number);

  return (
    <div>
      <div className="flex items-start justify-between mb-8 flex-wrap gap-2">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Gestión de cursos</h2>
        </div>
        <button onClick={abrirNuevoCurso}
          className="px-4 py-2 bg-primary text-white text-sm font-semibold  hover:bg-primary-hover transition-colors cursor-pointer">
          + Nuevo curso
        </button>
      </div>

      {mensaje && <div className="mb-6 p-3 bg-green-50 border border-green-200 text-green-700 text-sm ">{mensaje}</div>}
      {error && <div className="mb-6 p-3 bg-red-50 border border-red-200 text-red-700 text-sm ">{error}</div>}

      {/* Cursos */}
      <div className="bg-white  border border-gray-200 table-container mb-8">
        <div className="p-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Cursos</h3>
        </div>
        {cargando ? (
          <p className="text-sm text-gray-500 p-4">Cargando cursos...</p>
        ) : cursos.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-8">No hay cursos registrados.</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">ID</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Nombre</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Código</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Créditos</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">H. lectivas</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">H. prácticas</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {cursos.map(c => (
                <tr key={c.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-900 font-medium">{c.id}</td>
                  <td className="px-4 py-3 text-gray-700">{c.nombre}</td>
                  <td className="px-4 py-3 text-gray-500">{c.codigo}</td>
                  <td className="px-4 py-3 text-gray-600">{c.creditos}</td>
                  <td className="px-4 py-3 text-gray-600">{c.horas_lectivas}</td>
                  <td className="px-4 py-3 text-gray-600">{c.horas_practicas}</td>
                  <td className="px-4 py-3">
                    <div className="flex gap-1.5 flex-wrap">
                      <button onClick={() => abrirEditarCurso(c)}
                        className="px-2.5 py-1 text-xs font-semibold  border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 transition-colors cursor-pointer">
                        Editar
                      </button>
                      <button onClick={() => manejarEliminarCurso(c.id)}
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

      {/* Asignación a planes */}
      <div className="bg-white  border border-gray-200 table-container">
        <div className="p-4 border-b border-gray-200 flex items-center justify-between flex-wrap gap-2">
          <h3 className="text-lg font-semibold text-gray-900">Asignación de cursos a planes</h3>
          <div className="w-full md:w-auto">
            <select value={planSeleccionado} onChange={(e) => setPlanSeleccionado(e.target.value)}
              className="w-full md:w-64">
              <option value="">Seleccionar plan...</option>
              {planes.map(p => (
                <option key={p.id} value={p.id}>{p.nombre || `Plan #${p.id}`}</option>
              ))}
            </select>
          </div>
        </div>

        {!planSeleccionado ? (
          <p className="text-sm text-gray-500 text-center py-8">Selecciona un plan de estudios para ver sus cursos.</p>
        ) : (
          <>
            <div className="p-4 border-b border-gray-200 flex justify-end">
              <button onClick={() => { setAsignarForm({ semestre_id: "", curso_id: "" }); setModalAsignar(true); }}
                disabled={cursosNoAsignados.length === 0}
                className="px-3 py-1.5 text-xs font-semibold  bg-primary text-white hover:bg-primary-hover disabled:bg-gray-300 disabled:text-gray-500 transition-colors cursor-pointer">
                + Asignar curso
              </button>
            </div>
            {cursosPlan.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-8">Este plan no tiene cursos asignados.</p>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-50 border-b border-gray-200">
                    <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Semestre</th>
                    <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Curso</th>
                    <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Código</th>
                    <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Créditos</th>
                    <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {cursosPlan.map(cp => (
                    <tr key={cp.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-gray-900 font-medium">{cp.semestre_codigo}</td>
                      <td className="px-4 py-3 text-gray-700">{cp.curso_nombre}</td>
                      <td className="px-4 py-3 text-gray-500">{cp.curso_codigo}</td>
                      <td className="px-4 py-3 text-gray-600">{cp.creditos}</td>
                      <td className="px-4 py-3">
                        <button onClick={() => manejarEliminarCursoPlan(cp.id)}
                          className="px-2.5 py-1 text-xs font-semibold  bg-red-50 text-red-700 border border-red-200 hover:bg-red-100 transition-colors cursor-pointer">
                          Quitar
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </>
        )}
      </div>

      {/* Prerequisitos */}
      <div className="bg-white border border-gray-200 table-container mt-8">
        <div className="p-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Prerequisitos</h3>
        </div>
        <div className="p-4 border-b border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
            <div>
              <label>Curso que requiere prerequisito</label>
              <select value={cursoPreReq} onChange={(e) => { setCursoPreReq(e.target.value); setCursoReqSeleccionado(""); }}>
                <option value="">Seleccionar...</option>
                {cursos.map(c => <option key={c.id} value={c.id}>{c.nombre} ({c.codigo})</option>)}
              </select>
            </div>
            <div>
              <label>Curso requisito</label>
              <select value={cursoReqSeleccionado} onChange={(e) => setCursoReqSeleccionado(e.target.value)} disabled={!cursoPreReq}>
                <option value="">Seleccionar...</option>
                {cursos.filter(c => c.id !== Number(cursoPreReq)).map(c => (
                  <option key={c.id} value={c.id}>{c.nombre} ({c.codigo})</option>
                ))}
              </select>
            </div>
            <div>
              <button onClick={agregarPrerequisito} disabled={agregandoPreReq || !cursoPreReq || !cursoReqSeleccionado}
                className="px-4 py-2 bg-primary text-white text-sm font-semibold hover:bg-primary-hover disabled:bg-gray-300 disabled:text-gray-500 transition-colors cursor-pointer">
                {agregandoPreReq ? "Agregando..." : "Agregar prerequisito"}
              </button>
            </div>
          </div>
        </div>
        {cursosConPrerequisitos.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-8">No hay prerequisitos registrados.</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Curso</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Prerequisitos</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {cursos.map(c => {
                const reqs = prerequisitosPorCurso[c.id];
                if (!reqs) return null;
                return (
                  <tr key={c.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-gray-900 font-medium">{c.nombre} ({c.codigo})</td>
                    <td className="px-4 py-3">
                      <div className="flex gap-1.5 flex-wrap">
                        {reqs.map(reqId => (
                          <span key={reqId} className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs border border-gray-200 bg-gray-50 text-gray-700">
                            {nombreCurso(reqId)}
                            <button onClick={() => eliminarPrerequisitoHandler(c.id, reqId)}
                              className="text-gray-400 hover:text-red-600 cursor-pointer border-0 bg-transparent p-0 leading-none text-sm">&times;</button>
                          </span>
                        ))}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Modal curso */}
      {mostrarModalCurso && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center" onClick={() => setMostrarModalCurso(false)}>
          <div className="bg-white  shadow-xl p-6 w-full max-w-lg mx-4" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold text-gray-900 mb-4">{editandoCurso ? "Editar curso" : "Nuevo curso"}</h3>
            <form onSubmit={guardarCurso}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div className="md:col-span-2">
                  <label>Nombre *</label>
                  <input type="text" required value={cursoForm.nombre} onChange={(e) => setCursoForm({ ...cursoForm, nombre: e.target.value })} />
                </div>
                <div>
                  <label>Código *</label>
                  <input type="text" required value={cursoForm.codigo} onChange={(e) => setCursoForm({ ...cursoForm, codigo: e.target.value })} />
                </div>
                <div>
                  <label>Créditos *</label>
                  <input type="number" required min={1} value={cursoForm.creditos} onChange={(e) => setCursoForm({ ...cursoForm, creditos: e.target.value })} />
                </div>
                <div>
                  <label>Horas lectivas</label>
                  <input type="number" min={0} value={cursoForm.horas_lectivas} onChange={(e) => setCursoForm({ ...cursoForm, horas_lectivas: e.target.value })} />
                </div>
                <div>
                  <label>Horas prácticas</label>
                  <input type="number" min={0} value={cursoForm.horas_practicas} onChange={(e) => setCursoForm({ ...cursoForm, horas_practicas: e.target.value })} />
                </div>
              </div>
              <div className="flex gap-3 justify-end mt-6">
                <button type="button" onClick={() => setMostrarModalCurso(false)}
                  className="px-4 py-2 text-sm font-semibold  border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 transition-colors cursor-pointer">
                  Cancelar
                </button>
                <button type="submit" disabled={guardando}
                  className="px-4 py-2 text-sm font-semibold  bg-primary text-white hover:bg-primary-hover disabled:bg-gray-300 disabled:text-gray-500 transition-colors cursor-pointer">
                  {guardando ? "Guardando..." : editandoCurso ? "Actualizar" : "Crear curso"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal asignar curso a plan */}
      {modalAsignar && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center" onClick={() => setModalAsignar(false)}>
          <div className="bg-white  shadow-xl p-6 w-full max-w-sm mx-4" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold text-gray-900 mb-4">Asignar curso al plan</h3>
            <div className="mb-4">
              <label>Semestre</label>
              <select value={asignarForm.semestre_id} onChange={(e) => setAsignarForm({ ...asignarForm, semestre_id: e.target.value })}>
                <option value="">Seleccionar...</option>
                {semestres.map(s => (<option key={s.id} value={s.id}>{s.codigo}</option>))}
              </select>
            </div>
            <div className="mb-4">
              <label>Curso</label>
              <select value={asignarForm.curso_id} onChange={(e) => setAsignarForm({ ...asignarForm, curso_id: e.target.value })}>
                <option value="">Seleccionar...</option>
                {cursosNoAsignados.map(c => (<option key={c.id} value={c.id}>{c.nombre} ({c.codigo})</option>))}
              </select>
            </div>
            <div className="flex gap-3 justify-end">
              <button onClick={() => setModalAsignar(false)}
                className="px-4 py-2 text-sm font-semibold  border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 transition-colors cursor-pointer">
                Cancelar
              </button>
              <button onClick={manejarAsignarCurso} disabled={asignando || !asignarForm.semestre_id || !asignarForm.curso_id}
                className="px-4 py-2 text-sm font-semibold  bg-primary text-white hover:bg-primary-hover disabled:bg-gray-300 disabled:text-gray-500 transition-colors cursor-pointer">
                {asignando ? "Asignando..." : "Asignar"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
