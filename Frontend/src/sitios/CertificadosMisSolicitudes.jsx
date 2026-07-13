import { useState, useEffect } from "react";
import { misSolicitudes, urlDescargarCertificado } from "../servicios/certificados.servicio";

function colorEstado(estado) {
  if (estado === "Pendiente de Validación") return "bg-yellow-50 text-yellow-700 border-yellow-200";
  if (estado === "Apto para Firma") return "bg-blue-50 text-blue-700 border-blue-200";
  if (estado === "Emitido") return "bg-green-50 text-green-700 border-green-200";
  if (estado === "Rechazado") return "bg-red-50 text-red-700 border-red-200";
  return "bg-gray-50 text-gray-600 border-gray-200";
}

export default function CertificadosMisSolicitudes() {
  const [solicitudes, setSolicitudes] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    cargar();
  }, []);

  async function cargar() {
    setCargando(true);
    const { data, error } = await misSolicitudes();
    setCargando(false);
    if (error) { setError(error); return; }
    setSolicitudes(data || []);
  }

  return (
    <div>
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900">Mis solicitudes de certificados</h2>
        <p className="text-sm text-gray-500 mt-1">Estado de cada trámite</p>
      </div>

      {error && <div className="mb-6 p-3 bg-red-50 border border-red-200 text-red-700 text-sm">{error}</div>}

      {cargando ? (
        <div className="bg-white border border-gray-200 p-6">
          <p className="text-sm text-gray-500">Cargando...</p>
        </div>
      ) : solicitudes.length === 0 ? (
        <div className="bg-white border border-gray-200 p-6">
          <p className="text-sm text-gray-500">No has solicitado ning&uacute;n certificado a&uacute;n.</p>
        </div>
      ) : (
        <div className="bg-white border border-gray-200 table-container">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">#</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Tipo</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Estado</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Fecha</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Acci&oacute;n</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {solicitudes.map((s) => (
                <tr key={s.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-900 font-medium">{s.id}</td>
                  <td className="px-4 py-3 text-gray-600">{s.tipo}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center px-2.5 py-0.5 text-xs font-medium border ${colorEstado(s.estado)}`}>
                      {s.estado}
                    </span>
                    {s.motivo_rechazo && (
                      <p className="text-xs text-red-600 mt-1">{s.motivo_rechazo}</p>
                    )}
                  </td>
                  <td className="px-4 py-3 text-xs text-gray-500">{s.fecha_creacion ? new Date(s.fecha_creacion).toLocaleDateString() : "—"}</td>
                  <td className="px-4 py-3">
                    {s.estado === "Emitido" ? (
                      <a
                        href={urlDescargarCertificado(s.id)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center px-3 py-1.5 text-xs font-semibold bg-primary text-white hover:bg-primary-hover transition-colors no-underline"
                      >
                        Descargar PDF
                      </a>
                    ) : s.estado === "Rechazado" ? (
                      <span className="text-xs text-gray-400">Rechazado</span>
                    ) : (
                      <span className="text-xs text-gray-400">En tr&aacute;mite</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}