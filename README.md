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
python3 -m venv .venv
source .venv/bin/activate  # En Windows usar .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

La aplicación expone la API en `http://localhost:8000/api/*` y sirve la interfaz web en `http://localhost:8000/`.

## Configuración de credenciales de Strava

1. Crea una aplicación en [https://www.strava.com/settings/api](https://www.strava.com/settings/api).
2. Define como **Authorization Callback Domain** la URL de tu backend (por ejemplo `localhost` o el dominio público si ya está desplegado).
3. Copia el `Client ID` y `Client Secret` generados y duplíca el archivo `.env.example` ubicado en la raíz del proyecto:

   ```bash
   cp .env.example .env
   ```

   Edita `.env` y reemplaza los valores por los datos reales que te entregó Strava (por ejemplo el `Client Secret` `dee859205f14967862b3062a256b47f17e1624d3`). **Nunca subas este archivo al repositorio**.

4. (Opcional) Actualiza `STRAVA_REDIRECT_URI` si expones la aplicación en otro host/puerto y ajusta `STRAVA_SCOPE` según el alcance requerido (con el alcance `read` que compartiste es suficiente para validar la sesión).

5. Reinicia `uvicorn` para que cargue las nuevas variables (el proyecto utiliza `python-dotenv`).

> ℹ️ No necesitas configurar manualmente el *access token* ni el *refresh token* (`b88a316abcee3ffff2ec0aa5675967a7dbd7a3e6` / `36e63e9526e0b31fc80d1087bd40354e599672e2`). Al completar el inicio de sesión, la API los guardará automáticamente en `team_wolf_tracking.db` y los refrescará cuando caduquen.

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
2. Añadir autenticación para limitar quién puede registrar actividades (OAuth de Google, contraseñas o integración con Strava).
3. Desplegar en un servicio gestionado (Railway, Render, Fly.io, etc.) y configurar HTTPS automático.
4. Construir dashboards adicionales a partir del endpoint `/api/summary` o consumir la API desde herramientas BI.
5. Convertir la interfaz en PWA y generar exportaciones CSV/Excel para reportes offline.

## Documentación ampliada

- [Manual paso a paso de implementación y uso](docs/MANUAL_IMPLEMENTACION_Y_USO.md): guía detallada para preparar el entorno, ejecutar la app, registrar actividades, probar el login con Strava y aplicar las mejoras recomendadas.
