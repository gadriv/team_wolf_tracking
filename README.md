# Team Wolf Tracking

Aplicación ligera para reemplazar los formularios de Google y centralizar el registro de actividades deportivas del equipo.

## Características

- Registro de actividades con nombre del atleta, tipo de entrenamiento, duración, intensidad, lugar, fecha y notas.
- Panel de métricas automáticas (total de sesiones, minutos acumulados, atletas únicos y actividad más frecuente).
- Base de datos SQLite local lista para sincronizarse posteriormente con otras fuentes (por ejemplo Google Sheets o BigQuery).
- API REST construida con FastAPI para integrarse con otras aplicaciones o automatizaciones.
- Botón de conexión con Strava para iniciar sesión mediante OAuth y almacenar los tokens del atleta en SQLite.

## Requisitos

- Python 3.11+
- Dependencias listadas en `requirements.txt`

## Cómo ejecutar

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows usar .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

La aplicación expone la API en `http://localhost:8000/api/*` y sirve la interfaz web en `http://localhost:8000/`.

## Configuración de credenciales de Strava

1. Crea una aplicación en [https://www.strava.com/settings/api](https://www.strava.com/settings/api).
2. Define como **Authorization Callback Domain** la URL de tu backend (por ejemplo `localhost` o el dominio público si ya está desplegado).
3. Copia el `Client ID` y `Client Secret` generados y crea un archivo `.env` en la raíz con el siguiente contenido:

   ```env
   STRAVA_CLIENT_ID=tu_id
   STRAVA_CLIENT_SECRET=tu_secret
   STRAVA_REDIRECT_URI=http://localhost:8000/api/auth/strava/callback  # ajusta si expones otro host/puerto
   STRAVA_SCOPE=read,activity:read,profile:read_all  # opcional
   ```

4. Reinicia `uvicorn` para que cargue las nuevas variables (el proyecto utiliza `python-dotenv`).

### Probar el inicio de sesión con Strava

1. Abre `http://localhost:8000` y presiona **Conectar con Strava**.
2. Serás redirigido al flujo oficial de Strava; acepta los permisos solicitados.
3. Al regresar al backend, se almacenará/actualizará el registro en la tabla `stravaaccount` dentro del archivo `team_wolf_tracking.db`.
4. Puedes verificar el último acceso ejecutando `sqlite3 team_wolf_tracking.db "select strava_athlete_id, athlete_full_name, token_expires_at from stravaaccount;"` o consultando el endpoint `GET /api/auth/strava/callback` con un navegador después de la autorización (la respuesta muestra el nombre del atleta y la expiración del token).

## Endpoints principales

| Método | Ruta | Descripción |
| --- | --- | --- |
| `GET` | `/api/activities` | Listado completo de actividades |
| `POST` | `/api/activities` | Crea un nuevo registro |
| `GET` | `/api/summary` | Estadísticas agregadas |
| `GET` | `/api/auth/strava/login` | Genera la URL de autorización de Strava |
| `GET` | `/api/auth/strava/callback` | Guarda tokens tras la autorización |
| `GET` | `/health` | Healthcheck para monitoreo |

## Cómo probar en Android, iOS, macOS y Windows

1. Ejecuta el servidor con `uvicorn app.main:app --host 0.0.0.0 --port 8000` para que acepte conexiones de otros dispositivos de tu red.
2. Identifica la IP local de la máquina anfitriona (ej. `192.168.1.10`).
3. En cada plataforma abre `http://IP_LOCAL:8000` en el navegador.

- **Android**: conéctate a la misma Wi-Fi, abre Chrome/Firefox y navega a la IP. Puedes agregar la página a la pantalla principal para tener un acceso directo estilo app.
- **iOS**: usa Safari, acepta el certificado si usas HTTPS propio o mantente en HTTP durante las pruebas locales. Agrega el sitio a la pantalla de inicio para simular un PWA.
- **macOS**: utiliza Terminal (`python -m venv .venv && source .venv/bin/activate`) y ejecuta los comandos anteriores. Safari o Chrome pueden acceder a `http://localhost:8000` directamente.
- **Windows**: abre *PowerShell* como administrador, ejecuta `py -3 -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt; uvicorn app.main:app --reload`. Navega con Edge/Chrome y, si necesitas exponerlo a dispositivos móviles, asegúrate de permitir el puerto 8000 en el Firewall.

## Próximos pasos sugeridos

1. Conectar la API con Google Sheets usando `gspread` o la API oficial para mantener sincronización con hojas existentes.
2. Añadir autenticación para limitar quién puede registrar actividades.
3. Desplegar en un servicio gestionado (Railway, Render, Fly.io, etc.).
4. Construir dashboards adicionales a partir del endpoint `/api/summary`.
