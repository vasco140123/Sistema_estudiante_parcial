import { useState } from "react";
import { useNavigate, Navigate } from "react-router-dom";
import { iniciarSesion as loginServicio } from "../servicios/auth.servicio";
import { useAuth } from "../context/AuthContext";

// ── Íconos SVG ────────────────────────────────────────────────────────────────
const IconUser = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
    <circle cx="12" cy="7" r="4"/>
  </svg>
);

const IconLock = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
  </svg>
);

// ── Estilos ───────────────────────────────────────────────────────────────────
const S = {
  page: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "var(--bg-body)",
    padding: "24px 16px",
    fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
    transition: "background-color 0.2s ease",
  },
  card: {
    width: "100%",
    maxWidth: "400px",
    backgroundColor: "var(--bg-card)",
    border: "1px solid var(--border-light)",
    padding: "40px 36px 36px",
    transition: "background-color 0.2s ease, border-color 0.2s ease",
  },
  cardHeader: {
    textAlign: "center",
    marginBottom: "32px",
  },
  title: {
    fontSize: "22px",
    fontWeight: "700",
    color: "#059669",
    margin: "0 0 4px 0",
    lineHeight: 1.2,
  },
  subtitle: {
    fontSize: "13px",
    fontWeight: "400",
    color: "var(--text-muted)",
    margin: 0,
  },
  fieldGroup: {
    marginBottom: "16px",
  },
  label: {
    display: "block",
    fontSize: "12px",
    fontWeight: "600",
    color: "var(--text-muted)",
    marginBottom: "6px",
  },
  inputWrapper: {
    position: "relative",
    display: "flex",
    alignItems: "center",
  },
  iconLeft: {
    position: "absolute",
    left: "12px",
    color: "var(--text-muted-light)",
    display: "flex",
    alignItems: "center",
    pointerEvents: "none",
  },
  input: {
    width: "100%",
    padding: "10px 12px 10px 36px",
    border: "1.5px solid var(--border-light)",
    borderRadius: "0",
    fontSize: "14px",
    fontWeight: "400",
    color: "var(--text-primary)",
    backgroundColor: "var(--bg-input)",
    outline: "none",
    fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
    transition: "border-color 0.15s ease, background-color 0.2s ease, color 0.2s ease",
  },
  inputPassword: {
    width: "100%",
    padding: "10px 12px 10px 36px",
    border: "1.5px solid var(--border-light)",
    borderRadius: "0",
    fontSize: "14px",
    fontWeight: "400",
    color: "var(--text-primary)",
    backgroundColor: "var(--bg-input)",
    outline: "none",
    fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
    transition: "border-color 0.15s ease, background-color 0.2s ease, color 0.2s ease",
  },
  btnSubmit: {
    width: "100%",
    padding: "12px",
    marginTop: "8px",
    backgroundColor: "#059669",
    color: "#ffffff",
    border: "none",
    borderRadius: "0",
    fontSize: "14px",
    fontWeight: "600",
    cursor: "pointer",
    fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
    transition: "background-color 0.15s ease",
  },
  btnSubmitDisabled: {
    backgroundColor: "#d1d5db",
    color: "#9ca3af",
    cursor: "not-allowed",
  },
  errorBox: {
    marginTop: "16px",
    padding: "10px 14px",
    backgroundColor: "#fef2f2",
    border: "1.5px solid #fecaca",
    color: "#dc2626",
    fontSize: "13px",
    fontWeight: "500",
  },
};

// ── Componente ────────────────────────────────────────────────────────────────
export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [cargando, setCargando] = useState(false);
  const { iniciarSesion, estaAutenticado } = useAuth();
  const navigate = useNavigate();

  if (estaAutenticado) return <Navigate to="/" replace />;

  async function manejarEnvio(e) {
    e.preventDefault();
    setError(null);
    setCargando(true);
    const { data, error } = await loginServicio(username, password);
    setCargando(false);
    if (error) { setError(error); return; }
    iniciarSesion(data.usuario, data.token);
    navigate("/");
  }

  return (
    <div style={S.page}>
      <div style={S.card}>
        <div style={S.cardHeader}>
          <h1 style={S.title}>Iniciar sesión</h1>
          <p style={S.subtitle}>Sistema Académico</p>
        </div>

        <form onSubmit={manejarEnvio} noValidate>
          <div style={S.fieldGroup}>
            <label style={S.label} htmlFor="login-username">Usuario</label>
            <div style={S.inputWrapper}>
              <span style={S.iconLeft}><IconUser /></span>
              <input
                id="login-username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Ingrese su usuario"
                required
                autoComplete="username"
                style={S.input}
              />
            </div>
          </div>

          <div style={{ ...S.fieldGroup, marginBottom: "24px" }}>
            <label style={S.label} htmlFor="login-password">Contraseña</label>
            <div style={S.inputWrapper}>
              <span style={S.iconLeft}><IconLock /></span>
              <input
                id="login-password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Ingrese su contraseña"
                required
                autoComplete="current-password"
                style={S.inputPassword}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={cargando}
            style={{
              ...S.btnSubmit,
              ...(cargando ? S.btnSubmitDisabled : {}),
            }}
            onMouseEnter={(e) => { if (!cargando) e.currentTarget.style.backgroundColor = "#047857"; }}
            onMouseLeave={(e) => { if (!cargando) e.currentTarget.style.backgroundColor = "#059669"; }}
          >
            {cargando ? "Ingresando…" : "Ingresar"}
          </button>
        </form>

        {error && <div style={S.errorBox}>{error}</div>}
      </div>
    </div>
  );
}
