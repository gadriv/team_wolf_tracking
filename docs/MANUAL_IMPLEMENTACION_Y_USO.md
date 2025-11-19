# Manual paso a paso de implementación y uso

Este documento describe, en español y con instrucciones detalladas, cómo desplegar, configurar y operar la aplicación Team Wolf Tracking que reemplaza los formularios de Google. Además, incluye recomendaciones de mejora para continuar la evolución del producto.

## 1. Resumen funcional

- Registro de sesiones deportivas con campos obligatorios (atleta, fecha, tipo de actividad, duración, intensidad, lugar y notas).
- Panel web con métricas agregadas en tiempo real.
- API REST con endpoints públicos para registrar y consultar datos.
- Integración OAuth con Strava para vincular cuentas y reutilizar los datos de entrenamiento.
- Persistencia en una base de datos SQLite local (`team_wolf_tracking.db`).

## 2. Prerrequisitos

1. **Python 3.11 o superior** instalado en el equipo anfitrión.
2. Acceso a internet para descargar dependencias (FastAPI, Uvicorn, httpx, etc.).
3. (Opcional) Cuenta de desarrollador en Strava para habilitar el inicio de sesión.
4. Acceso a la red local/Wi-Fi compartida si se desea probar desde móviles.

## 3. Preparar el entorno de trabajo

1. Clona o descarga el repositorio en tu equipo:
   ```bash
   git clone <URL_DEL_REPO>
   cd team_wolf_tracking
   ```
2. Crea y activa un entorno virtual aislado:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Windows usa .venv\Scripts\activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## 4. Configurar variables de entorno y Strava

1. Regístrate en [https://www.strava.com/settings/api](https://www.strava.com/settings/api) y crea una nueva aplicación.
2. Define como **Authorization Callback Domain** el dominio (o IP) donde correrá tu backend.
3. Duplica el archivo `.env.example` incluido en la raíz del repositorio y renómbralo a `.env`:
   ```bash
   cp .env.example .env
   ```
4. Abre `.env` y pega los valores reales provistos por Strava. Por ejemplo:
   ```env
   STRAVA_CLIENT_ID=123456
   STRAVA_CLIENT_SECRET=dee859205f14967862b3062a256b47f17e1624d3
   STRAVA_REDIRECT_URI=http://localhost:8000/api/auth/strava/callback
   STRAVA_SCOPE=read
   ```
   - Usa el `Client ID` y `Client Secret` de tu app.
   - El alcance `read` que compartiste es suficiente para validar el inicio de sesión; puedes ampliarlo si luego importas actividades.
   - Los *access/refresh tokens* (`b88a316abcee3ffff2ec0aa5675967a7dbd7a3e6` / `36e63e9526e0b31fc80d1087bd40354e599672e2`) **no van en el `.env`**: se obtienen y almacenan automáticamente cuando completes el flujo de login.
5. Si despliegas en producción, añade también variables para el host/puerto (ej. `PORT=80`).
6. Reinicia el servidor cada vez que actualices el archivo `.env` para cargar los nuevos valores.

## 5. Inicializar la base de datos

1. La primera ejecución creará automáticamente `team_wolf_tracking.db` en la raíz del proyecto.
2. Para inspeccionar la estructura puedes usar `sqlite3`:
   ```bash
   sqlite3 team_wolf_tracking.db ".tables"
   sqlite3 team_wolf_tracking.db "PRAGMA table_info(activity);"
   ```
3. Haz respaldos periódicos copiando el archivo `.db` a un almacenamiento seguro.

## 6. Ejecutar la aplicación localmente

1. Lanza el servidor con:
   ```bash
   uvicorn app.main:app --reload
   ```
2. Accede a la interfaz web en `http://localhost:8000/`.
3. El API queda disponible bajo `http://localhost:8000/api/*` y la documentación interactiva en `http://localhost:8000/docs`.

## 7. Registrar actividades desde la interfaz

1. Completa el formulario principal con los datos del entrenamiento.
2. Presiona **Guardar** y espera el mensaje de confirmación.
3. El panel lateral actualizará automáticamente las métricas agregadas.
4. Las actividades aparecen en la tabla inferior; puedes refrescar la página para validar la persistencia.

## 8. Consumir la API manualmente

- **Listar actividades:**
  ```bash
  curl http://localhost:8000/api/activities
  ```
- **Crear actividad vía JSON:**
  ```bash
  curl -X POST http://localhost:8000/api/activities \
       -H "Content-Type: application/json" \
       -d '{
         "athlete_name": "Ana",
         "activity_type": "Natación",
         "duration_minutes": 45,
         "intensity": "Media",
         "location": "Piscina Municipal",
         "date": "2024-05-01",
         "notes": "Series de técnica"
       }'
  ```
- **Consultar métricas:**
  ```bash
  curl http://localhost:8000/api/summary
  ```

## 9. Iniciar sesión con Strava

1. Desde la UI, haz clic en **Conectar con Strava**.
2. Autoriza la aplicación en la página oficial de Strava.
3. Al volver al backend, los tokens se almacenan en la tabla `stravaaccount`.
4. Repite el proceso si necesitas refrescar los permisos o actualizar los datos del atleta.

## 10. Pruebas multi-plataforma

1. Ejecuta `uvicorn app.main:app --host 0.0.0.0 --port 8000` para permitir conexiones en la red local.
2. Identifica la IP del servidor (por ejemplo `192.168.1.10`).
3. En cada dispositivo abre `http://IP_LOCAL:8000`:
   - **Android:** usa Chrome/Firefox y, si deseas comportamiento tipo app, agrega la página a la pantalla principal.
   - **iOS:** navega con Safari y autoriza certificados locales si utilizas HTTPS propio.
   - **macOS/Windows:** abre un navegador moderno (Safari, Edge, Chrome) y verifica tanto la UI como la documentación Swagger.

## 11. Despliegue en producción (resumen)

1. Usa un servicio como Railway, Render o Fly.io que soporte apps ASGI.
2. Define variables de entorno seguras (sin subir secretos al repositorio).
3. Configura HTTPS mediante certificados gestionados por la plataforma.
4. Habilita un proceso de despliegue continuo (GitHub Actions, etc.) para automatizar pruebas y publicación.

## 12. Mantenimiento y monitoreo

- Programa respaldos automáticos del archivo SQLite o migra a PostgreSQL/MySQL cuando aumente el tráfico.
- Implementa logs estructurados (ej. `uvicorn --log-level info`) y recolecta métricas con servicios como Grafana o BetterStack.
- Documenta cada versión del esquema y aplica migraciones controladas si cambian los campos de `activity`.

## 13. Posibles mejoras recomendadas

1. **Autenticación y roles**: añadir inicio de sesión propio (por ejemplo con OAuth de Google o contraseñas) para restringir el acceso.
2. **Integración con Google Sheets**: sincronizar las tablas con las hojas históricas usando la API oficial o `gspread`.
3. **Notificaciones automáticas**: enviar recordatorios por correo/WhatsApp cuando un atleta no registre sesiones en un periodo determinado.
4. **Exportaciones**: generar reportes en CSV/Excel desde el endpoint `/api/activities` para análisis offline.
5. **PWA / App híbrida**: convertir la interfaz en una Progressive Web App para ofrecer experiencia nativa en móviles.
6. **Dashboard avanzado**: construir vistas adicionales (por ejemplo gráficas semanales) sobre `/api/summary` o conectando herramientas BI.
7. **Sincronización con Strava**: ampliar el uso de los tokens para importar actividades automáticamente y evitar registros manuales.

---
Este manual debe mantenerse junto al código fuente para guiar a nuevos colaboradores y usuarios finales. Actualízalo cada vez que cambien los procesos descritos.
