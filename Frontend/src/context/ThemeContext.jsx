import { createContext, useContext, useState, useEffect } from "react";

const ThemeContext = createContext(null);

export function ThemeProvider({ children }) {
  const [oscuro, setOscuro] = useState(() => {
    const guardado = localStorage.getItem("tema");
    return guardado === "oscuro";
  });

  useEffect(() => {
    document.documentElement.classList.toggle("dark", oscuro);
    localStorage.setItem("tema", oscuro ? "oscuro" : "claro");
  }, [oscuro]);

  function toggleTema() {
    setOscuro((prev) => !prev);
  }

  return (
    <ThemeContext.Provider value={{ oscuro, toggleTema }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTema() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTema debe usarse dentro de ThemeProvider");
  return ctx;
}
