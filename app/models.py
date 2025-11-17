from datetime import datetime, date
from typing import Optional

from sqlmodel import Field, SQLModel


class Activity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    athlete_name: str = Field(index=True, description="Nombre del atleta que registra la actividad")
    activity_type: str = Field(description="Tipo de actividad o entrenamiento")
    duration_minutes: int = Field(description="Duración en minutos")
    intensity_level: str = Field(description="Nivel de intensidad percibido")
    location: Optional[str] = Field(default=None, description="Lugar donde se realizó la actividad")
    activity_date: date = Field(description="Fecha en la que ocurrió la actividad")
    notes: Optional[str] = Field(default=None, description="Comentarios adicionales")
    created_at: datetime = Field(default_factory=datetime.utcnow)
