from collections import Counter

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.database import get_session
from app.models import Activity
from app.schemas import ActivityCreate, ActivityRead, SummaryResponse

router = APIRouter(prefix="/api", tags=["activities"])


@router.get("/activities", response_model=list[ActivityRead])
def list_activities() -> list[ActivityRead]:
    with get_session() as session:
        statement = select(Activity).order_by(Activity.activity_date.desc(), Activity.created_at.desc())
        result = session.exec(statement).all()
    return result


@router.post("/activities", response_model=ActivityRead, status_code=status.HTTP_201_CREATED)
def create_activity(payload: ActivityCreate) -> ActivityRead:
    activity = Activity(**payload.dict())
    with get_session() as session:
        session.add(activity)
        session.flush()
        session.refresh(activity)
    return activity


@router.get("/activities/{activity_id}", response_model=ActivityRead)
def get_activity(activity_id: int) -> ActivityRead:
    with get_session() as session:
        activity = session.get(Activity, activity_id)
        if not activity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actividad no encontrada")
    return activity


@router.get("/summary", response_model=SummaryResponse)
def summary() -> SummaryResponse:
    with get_session() as session:
        activities = session.exec(select(Activity)).all()

    total_sessions = len(activities)
    total_minutes = sum(activity.duration_minutes for activity in activities)
    unique_athletes = len({activity.athlete_name for activity in activities})
    favorite_activity = None
    if activities:
        favorite_activity = Counter(activity.activity_type for activity in activities).most_common(1)[0][0]

    return SummaryResponse(
        total_sessions=total_sessions,
        total_minutes=total_minutes,
        unique_athletes=unique_athletes,
        favorite_activity=favorite_activity,
    )
