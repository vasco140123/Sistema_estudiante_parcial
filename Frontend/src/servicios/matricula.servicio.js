import { peticion, URL_BASE } from "./api";

export async function solicitarMatricula(seccionesCursoIds, comprobante) {
  if (comprobante) {
    const token = localStorage.getItem("token");
    const formData = new FormData();
    formData.append("secciones_curso_ids", seccionesCursoIds.join(","));
    formData.append("comprobante", comprobante);
    try {
      const resp = await fetch(`${URL_BASE}/matriculas/`, {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: formData,
      });
      const datos = await resp.json().catch(() => null);
      if (!resp.ok) return { data: null, error: datos?.error || "Error al enviar" };
      return { data: datos, error: null };
    } catch {
      return { data: null, error: "No se pudo conectar con el servidor" };
    }
  }
  return peticion("/matriculas/", {
    method: "POST",
    body: JSON.stringify({ secciones_curso_ids: seccionesCursoIds }),
  });
}

export async function listarMatriculas() {
  return peticion("/matriculas/");
}

export async function listarPeriodos() {
  return peticion("/matriculas/periodos");
}

export async function obtenerPeriodoActual() {
  return peticion("/matriculas/periodo-actual");
}

export async function obtenerCursosDisponibles() {
  return peticion("/matriculas/cursos-disponibles");
}

export async function listarSecciones() {
  return peticion("/matriculas/secciones");
}

export async function listarEstadosMatricula() {
  return peticion("/matriculas/estados");
}

export async function validarRequisitos(matriculaId) {
  return peticion(`/matriculas/${matriculaId}/validar`, { method: "PUT" });
}

export async function registrarPago(matriculaId) {
  return peticion(`/matriculas/${matriculaId}/pago`, { method: "POST" });
}

export async function generarFichaOficial(matriculaId) {
  return peticion(`/matriculas/${matriculaId}/ficha-oficial`, { method: "POST" });
}

export async function rechazarMatricula(matriculaId) {
  return peticion(`/matriculas/${matriculaId}/rechazar`, { method: "PUT" });
}

export async function obtenerEstadisticas() {
  return peticion("/matriculas/estadisticas");
}

export async function misMatriculas() {
  return peticion("/matriculas/mis-matriculas");
}

export function urlDescargarFicha(matriculaId) {
  const token = localStorage.getItem("token");
  return `${URL_BASE}/matriculas/${matriculaId}/ficha?token=${token}`;
}

export function urlDescargarComprobante(matriculaId) {
  const token = localStorage.getItem("token");
  return `${URL_BASE}/matriculas/${matriculaId}/comprobante?token=${token}`;
}