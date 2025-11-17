from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class ActivityBase(BaseModel):
    athlete_name: str = Field(..., min_length=1)
    activity_type: str = Field(..., min_length=1)
    duration_minutes: int = Field(..., gt=0)
    intensity_level: str = Field(..., min_length=1)
    location: Optional[str] = None
    activity_date: date
    notes: Optional[str] = Field(default=None, max_length=500)


class ActivityCreate(ActivityBase):
    pass


class ActivityRead(ActivityBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class SummaryResponse(BaseModel):
    total_sessions: int
    total_minutes: int
    unique_athletes: int
    favorite_activity: Optional[str]


class StravaAuthStartResponse(BaseModel):
    authorize_url: str
    state: str


class StravaAuthCallbackResponse(BaseModel):
    athlete_name: str
    strava_athlete_id: int
    access_token_expires_at: datetime
