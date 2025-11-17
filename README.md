# Team Wolf Tracking

Aplicación ligera para reemplazar los formularios de Google y centralizar el registro de actividades deportivas del equipo.

## Características

- Registro de actividades con nombre del atleta, tipo de entrenamiento, duración, intensidad, lugar, fecha y notas.
- Panel de métricas automáticas (total de sesiones, minutos acumulados, atletas únicos y actividad más frecuente).
- Base de datos SQLite local lista para sincronizarse posteriormente con otras fuentes (por ejemplo Google Sheets o BigQuery).
- API REST construida con FastAPI para integrarse con otras aplicaciones o automatizaciones.

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

## Endpoints principales

| Método | Ruta | Descripción |
| --- | --- | --- |
| `GET` | `/api/activities` | Listado completo de actividades |
| `POST` | `/api/activities` | Crea un nuevo registro |
| `GET` | `/api/summary` | Estadísticas agregadas |
| `GET` | `/health` | Healthcheck para monitoreo |

## Próximos pasos sugeridos

1. Conectar la API con Google Sheets usando `gspread` o la API oficial para mantener sincronización con hojas existentes.
2. Añadir autenticación para limitar quién puede registrar actividades.
3. Desplegar en un servicio gestionado (Railway, Render, Fly.io, etc.).
4. Construir dashboards adicionales a partir del endpoint `/api/summary`.
