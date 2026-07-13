import { useState, useEffect } from "react";
import { misMatriculas, urlDescargarFicha } from "../servicios/matricula.servicio";

export default function MisMatriculas() {
  const [matriculas, setMatriculas] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    cargar();
  }, []);

  async function cargar() {
    setCargando(true);
    const { data, error } = await misMatriculas();
    setCargando(false);
    if (error) { setError(error); return; }
    setMatriculas(data || []);
  }

  return (
    <div>
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900">Mis matr&iacute;culas</h2>
        <p className="text-sm text-gray-500 mt-1">Matr&iacute;culas confirmadas</p>
      </div>

      {error && <div className="mb-6 p-3 bg-red-50 border border-red-200 text-red-700 text-sm">{error}</div>}

      {cargando ? (
        <div className="bg-white border border-gray-200 p-6">
          <p className="text-sm text-gray-500">Cargando...</p>
        </div>
      ) : matriculas.length === 0 ? (
        <div className="bg-white border border-gray-200 p-6">
          <p className="text-sm text-gray-500">No tienes matr&iacute;culas confirmadas.</p>
        </div>
      ) : (
        <div className="bg-white border border-gray-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">N°</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Periodo</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Semestre</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Estado</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Pagado</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Ficha</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {matriculas.map((m) => (
                <tr key={m.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-900 font-medium">{m.id}</td>
                  <td className="px-4 py-3 text-gray-600">{m.periodo_academico_nombre}</td>
                  <td className="px-4 py-3 text-gray-600">{m.semestre_codigo}</td>
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center px-2.5 py-0.5 text-xs font-medium bg-green-50 text-green-700 border border-green-200">
                      {m.estado_nombre}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-xs font-medium ${m.pagado ? "text-green-600" : "text-red-600"}`}>
                      {m.pagado ? "Sí" : "No"}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <a
                      href={urlDescargarFicha(m.id)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center px-3 py-1.5 text-xs font-semibold bg-primary text-white hover:bg-primary-hover transition-colors no-underline"
                    >
                      Descargar PDF
                    </a>
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
