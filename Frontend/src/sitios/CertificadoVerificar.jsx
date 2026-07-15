import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { verificarCertificado } from "../servicios/certificados.servicio";

export default function CertificadoVerificar() {
  const { codigo } = useParams();
  const [resultado, setResultado] = useState(null);
  const [error, setError] = useState(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    if (codigo) {
      verificarCertificado(codigo).then(({ data, error }) => {
        setCargando(false);
        if (error) { setError(error); return; }
        setResultado(data);
      });
    }
  }, [codigo]);

  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="bg-white border border-gray-200 p-8 max-w-lg w-full">
        {cargando ? (
          <p className="text-center text-gray-500">Verificando certificado...</p>
        ) : error ? (
          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-4 flex items-center justify-center border-2 border-red-500">
              <span className="text-red-500 text-3xl font-bold">!</span>
            </div>
            <h2 className="text-xl font-bold text-red-600 mb-2">Certificado no válido</h2>
            <p className="text-sm text-gray-600">{error}</p>
          </div>
        ) : resultado?.valido ? (
          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-4 flex items-center justify-center border-2 border-green-500">
              <span className="text-green-500 text-3xl font-bold">&#10003;</span>
            </div>
            <h2 className="text-xl font-bold text-green-700 mb-4">Certificado verificado</h2>
            <div className="text-left space-y-2 text-sm">
              <p><strong>Tipo:</strong> {resultado.tipo}</p>
              <p><strong>Estudiante:</strong> {resultado.estudiante_nombre}</p>
              <p><strong>Fecha de emisión:</strong> {resultado.fecha_emision ? new Date(resultado.fecha_emision).toLocaleDateString() : "—"}</p>
              <p><strong>Hash:</strong> <span className="text-xs break-all">{resultado.hash_documento}</span></p>
            </div>
          </div>
        ) : resultado && !resultado.valido ? (
          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-4 flex items-center justify-center border-2 border-red-500">
              <span className="text-red-500 text-3xl font-bold">!</span>
            </div>
            <h2 className="text-xl font-bold text-red-600 mb-2">Certificado no válido</h2>
            <p className="text-sm text-gray-600">{resultado.mensaje || "El código de verificación no corresponde a un certificado emitido."}</p>
          </div>
        ) : null}
      </div>
    </div>
  );
}
