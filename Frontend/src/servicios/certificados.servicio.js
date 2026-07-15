import { peticion, URL_BASE } from "./api";

export async function listarSolicitudes() {
  return peticion("/certificados/bandeja");
}

export async function misSolicitudes() {
  return peticion("/certificados/mis-solicitudes");
}

export async function solicitarCertificado(datos) {
  if (datos.comprobante) {
    const token = localStorage.getItem("token");
    const formData = new FormData();
    formData.append("tipo", datos.tipo);
    formData.append("comprobante", datos.comprobante);
    try {
      const resp = await fetch(`${URL_BASE}/certificados/solicitar`, {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: formData,
      });
      const data = await resp.json().catch(() => null);
      if (!resp.ok) return { data: null, error: data?.error || "Error al enviar" };
      return { data, error: null };
    } catch {
      return { data: null, error: "No se pudo conectar con el servidor" };
    }
  }
  return peticion("/certificados/solicitar", {
    method: "POST",
    body: JSON.stringify(datos),
  });
}

export async function autorizarCertificado(certificadoId) {
  return peticion(`/certificados/${certificadoId}/autorizar`, {
    method: "PUT",
  });
}

export async function rechazarCertificado(certificadoId) {
  return peticion(`/certificados/tramite/rechazar`, {
    method: "PUT",
    body: JSON.stringify({ id: certificadoId }),
  });
}

export async function emitirCertificado(certificadoId) {
  return peticion(`/certificados/${certificadoId}/emitir`, {
    method: "POST",
  });
}

export async function verificarCertificado(codigo) {
  return peticion(`/certificados/verificar/${codigo}`);
}

export function urlQrCertificado(codigo) {
  return `${URL_BASE}/certificados/qr/${codigo}`;
}

export function urlDescargarCertificado(certificadoId) {
  return `${URL_BASE}/certificados/${certificadoId}/descargar`;
}

export async function descargarComprobante(certificadoId) {
  const token = localStorage.getItem("token");
  try {
    const resp = await fetch(`${URL_BASE}/certificados/${certificadoId}/comprobante`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!resp.ok) return { data: null, error: "No se pudo descargar el comprobante" };
    const blob = await resp.blob();
    const url = window.URL.createObjectURL(blob);
    const enlace = document.createElement("a");
    enlace.href = url;
    enlace.download = `comprobante_${certificadoId}.pdf`;
    enlace.click();
    window.URL.revokeObjectURL(url);
    return { data: true, error: null };
  } catch {
    return { data: null, error: "Error al descargar el comprobante" };
  }
}
