from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from app.api.activities import router as activities_router
from app.api.auth import router as auth_router
from app.database import init_db

app = FastAPI(title="Team Wolf Tracking", version="1.0.0")
load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(activities_router)
app.include_router(auth_router)

static_dir = Path(__file__).resolve().parent / "static"
init_db()
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


@app.get("/health", tags=["status"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
