from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import get_current_owner
from app.database import get_db
from app.models import Owner, Submission, Widget
from app.schemas import DashboardStats, SubmissionResponse


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/submissions", response_model=list[SubmissionResponse])
def dashboard_submissions(
    widget_id: int | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    owner: Owner = Depends(get_current_owner),
    database: Session = Depends(get_db),
):
    query = select(Submission).where(Submission.owner_id == owner.id)
    if widget_id is not None:
        query = query.where(Submission.widget_id == widget_id)
    return list(database.scalars(query.order_by(Submission.created_at.desc()).limit(limit)))


@router.get("/stats", response_model=DashboardStats)
def dashboard_stats(
    owner: Owner = Depends(get_current_owner),
    database: Session = Depends(get_db),
):
    total = database.scalar(
        select(func.count(Submission.id)).where(Submission.owner_id == owner.id)
    ) or 0
    widget_rows = database.execute(
        select(Widget.title, func.count(Submission.id))
        .join(Submission, Submission.widget_id == Widget.id, isouter=True)
        .where(Widget.owner_id == owner.id)
        .group_by(Widget.id, Widget.title)
    ).all()
    country_rows = database.execute(
        select(Submission.country, func.count(Submission.id))
        .where(Submission.owner_id == owner.id)
        .group_by(Submission.country)
    ).all()
    return DashboardStats(
        total_submissions=total,
        submissions_by_widget=[{"widget": title, "count": count} for title, count in widget_rows],
        submissions_by_country=[{"country": country or "Unknown", "count": count} for country, count in country_rows],
    )
