import { peticion } from "./api";

export async function listarCursos() {
  return peticion("/cursos");
}

export async function crearCurso(datos) {
  return peticion("/cursos", {
    method: "POST",
    body: JSON.stringify(datos),
  });
}

export async function actualizarCurso(id, datos) {
  return peticion(`/cursos/${id}`, {
    method: "PUT",
    body: JSON.stringify(datos),
  });
}

export async function eliminarCurso(id) {
  return peticion(`/cursos/${id}`, {
    method: "DELETE",
  });
}

export async function listarCursosPlan(planId) {
  return peticion(`/administracion/planes-estudio/${planId}/cursos`);
}

export async function asignarCursoPlan(planId, datos) {
  return peticion(`/administracion/planes-estudio/${planId}/cursos`, {
    method: "POST",
    body: JSON.stringify(datos),
  });
}

export async function eliminarCursoPlan(pcsId) {
  return peticion(`/administracion/planes-estudio/cursos/${pcsId}`, {
    method: "DELETE",
  });
}
