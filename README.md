# Sistema Académico Integral

Sistema de gestión académica para universidades que administra matrículas, notas, cursos, certificados, registro académico (kardex) y usuarios con control de acceso por roles.

## Equipo

- **Melgarejo Guzmán, Renzo Gustavo**
- **Ramos Mercado, Vasco Qory**

## Tecnologías

### Frontend

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| React | 19 | Librería de UI |
| Vite | 8 | Bundler y dev server |
| React Router DOM | 7 | Enrutamiento SPA |
| Tailwind CSS | 4 | Estilos utilitarios |
| Recharts | — | Gráficos y dashboards |
| React Icons | — | Iconos |

### Backend

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Python + Flask | 3.14 / 3.1 | Framework web |
| SQLAlchemy | 2.0 | ORM |
| Flask-Migrate / Alembic | 4.1 / 1.18 | Migraciones de BD |
| Flask-JWT-Extended | 4.7 | Autenticación JWT |
| Flask-Bcrypt | 1.0 | Hashing de contraseñas |
| PyMySQL | 1.2 | Driver MySQL |
| ReportLab | 5.0 | Generación de PDF |
| qrcode + Pillow | 8.2 / 12.3 | Códigos QR en certificados |

### Base de datos

- **MySQL** (configurable vía `DATABASE_URL`)
- 34 tablas normalizadas (usuarios, estudiantes, matrículas, cursos, notas, certificados, auditorías, etc.)

## Requisitos previos

- Python 3.10 o superior
- Node.js 18 o superior
- npm
- Git
- Servidor MySQL disponible

Verificar versiones:

```bash
python --version
node --version
npm --version
```

## Clonar el proyecto

```bash
git clone <URL-del-repositorio>
cd Sistema_estudiante_parcial
```

## Configurar el backend

```bash
cd Backend
python -m venv venv
```

Activar el entorno virtual:

- **Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`
- **Windows (CMD):** `.\venv\Scripts\activate.bat`
- **Linux/Mac:** `source venv/bin/activate`

Si PowerShell restringe la ejecución de scripts, ejecutar una sola vez:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Crear archivo `.env` en `Backend/`:

```env
DATABASE_URL=mysql+pymysql://usuario:contraseña@host/nombre_bd
```

Opcional — crear/recargar base de datos con datos de prueba:

```bash
python fresh.py
```

Iniciar servidor:

```bash
python run.py
```

El backend queda disponible en `http://127.0.0.1:5000`.

## Configurar el frontend

En otra terminal (dejando el backend corriendo):

```bash
cd Frontend
npm install
npm run dev
```

El frontend queda disponible en `http://localhost:5173`.

## Orden recomendado de ejecución

1. Configurar `.env` en `Backend/`
2. `pip install -r requirements.txt`
3. `python fresh.py` (base nueva + datos semilla)
4. `python run.py` (backend)
5. `npm install` (frontend)
6. `npm run dev` (frontend)

## Credenciales de prueba

Al ejecutar `python fresh.py` se crean los siguientes usuarios (contraseña: `123456`):

| Rol | Usuario |
|-----|---------|
| Estudiante | `estudiante_prueba` |
| Estudiante | `estudiante_prueba2` |
| Estudiante | `estudiante_prueba3` |
| Estudiante | `estudiante_prueba4` |
| Docente | `docente_prueba` |
| Docente | `docente_prueba2` |
| Docente | `docente_prueba3` |
| Docente | `docente_prueba4` |
| Administrador | `admin_prueba` |
| Dirección | `direccion_prueba` |

## Arquitectura del sistema

El sistema sigue una **arquitectura Cliente-Servidor** con frontend **SPA** y backend **REST API monolítico**. La comunicación es vía HTTP + JSON. La sesión se maneja con JWT y cada endpoint está protegido por rol mediante middleware.

### Arquitectura del backend (por capas)

```
Backend/app/
├── modelos/                  → Modelos ORM (SQLAlchemy) — 34 tablas
├── modulos/<modulo>/
│   ├── routes.py             → Definición de endpoints (Blueprint Flask)
│   ├── controllers.py        → Recibe HTTP, orquesta respuesta JSON
│   └── services.py           → Lógica de negocio y reglas
├── utils/
│   └── middlewares.py        → Decorador @rol_requerido (JWT + roles)
├── seeders/                  → Datos de prueba
└── config.py                 → Configuración desde variables de entorno
```

**Recorrido de un endpoint:** `ruta → controlador → servicio → modelo (ORM) → base de datos` y la respuesta regresa en sentido inverso como JSON.

### Estructura del frontend

```
Frontend/src/
├── sitios/                   → Páginas (una por ruta)
│   ├── Login.jsx
│   ├── Inicio.jsx
│   ├── SolicitarMatricula.jsx
│   ├── MisMatriculas.jsx
│   ├── ListarMatriculas.jsx
│   ├── EstadisticasMatricula.jsx
│   ├── CursosMisCursos.jsx
│   ├── CursosAsignar.jsx
│   ├── CursosCargaDocente.jsx
│   ├── NotasMiHoja.jsx
│   ├── NotasRegistrar.jsx
│   ├── NotasGestion.jsx
│   ├── RecordMiHistorial.jsx
│   ├── RecordReportes.jsx
│   ├── CertificadosSolicitar.jsx
│   ├── CertificadosMisSolicitudes.jsx
│   ├── CertificadosListar.jsx
│   ├── AdministracionUsuarios.jsx
│   ├── AdministracionAuditorias.jsx
│   └── GestionarCursos.jsx
├── componentes/              → UI reutilizable
│   ├── Layout.jsx            → Layout principal (sidebar + contenido)
│   ├── Sidebar.jsx           → Menú lateral con roles dinámicos
│   └── Navbar.jsx
├── servicios/                → Llamadas HTTP a la API (uno por módulo)
├── context/
│   ├── AuthContext.jsx        → Estado global de autenticación (JWT + usuario)
│   └── ThemeContext.jsx       → Tema oscuro/claro
├── rutas/
│   └── RutaProtegida.jsx     → Guard de rutas por rol
├── App.jsx                   → Definición de rutas (22 rutas)
└── main.jsx                  → Entry point (BrowserRouter + providers)
```

Cada página del frontend es independiente. El acceso está protegido por `RutaProtegida` según el rol, y el menú lateral se genera dinámicamente según el rol del usuario autenticado.

## Seguridad y control de acceso por roles

El sistema define **4 roles**: `estudiante`, `docente`, `administrador` y `direccion`.

- **Backend:** Cada endpoint está protegido con el decorador `@rol_requerido(rol1, rol2, ...)` que valida el JWT y verifica el rol.
- **Frontend:** `RutaProtegida` redirige al login si no hay sesión o muestra un error 403 si el rol no está autorizado. El `Sidebar` solo muestra las opciones del menú correspondientes al rol del usuario.

## Módulos implementados

| Módulo | Descripción | Roles |
|--------|-------------|-------|
| Autenticación | Login y sesión JWT | Todos |
| Dashboard | Inicio con estadísticas según el rol | Todos |
| Matrícula | Solicitud, validación, pagos y ficha oficial | Estudiante, Admin, Dirección |
| Cursos y Docentes | Asignación de docentes, horarios y carga docente | Docente, Admin, Dirección |
| Notas | Registro, consulta y gestión de actas | Docente, Estudiante, Admin, Dirección |
| Récord Académico | Historial académico, kardex y reportes PDF | Estudiante, Admin, Dirección |
| Certificados | Solicitud, aprobación y firma digital con QR | Estudiante, Admin, Dirección |
| Administración | Usuarios, roles, planes de estudio y cursos | Admin, Dirección |
| Auditoría | Bitácora de cambios y resumen estratégico | Dirección |
