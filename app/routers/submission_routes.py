from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import BackgroundJob, Submission, Widget
from app.schemas import LeadSubmission
from app.services.geo import enrich_ip
from app.services.jobs import process_confirmation_job
from app.services.rate_limit import is_rate_limited


router = APIRouter(tags=["Public submissions"])


@router.post("/public/widgets/{public_id}/submissions", status_code=status.HTTP_201_CREATED)
def submit_lead(
    public_id: str,
    payload: LeadSubmission,
    request: Request,
    background_tasks: BackgroundTasks,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=8, max_length=100),
    database: Session = Depends(get_db),
):
    widget = database.scalar(select(Widget).where(Widget.public_id == public_id, Widget.active.is_(True)))
    if widget is None:
        raise HTTPException(status_code=404, detail="Widget not found")

    ip_address = request.client.host if request.client else "unknown"
    if is_rate_limited(f"{ip_address}:{widget.id}"):
        raise HTTPException(status_code=429, detail="Submission rate limit exceeded")

    existing = database.scalar(
        select(Submission).where(
            Submission.widget_id == widget.id,
            Submission.idempotency_key == idempotency_key,
        )
    )
    if existing:
        return {"status": "already_processed", "submission_id": existing.id}

    if payload.company_website.strip():
        return {"status": "accepted"}

    geo = enrich_ip(ip_address)
    submission = Submission(
        widget_id=widget.id,
        owner_id=widget.owner_id,
        idempotency_key=idempotency_key,
        name=payload.name,
        email=str(payload.email),
        message=payload.message,
        ip_address=ip_address,
        country=geo.country if geo else None,
        city=geo.city if geo else None,
        geo_provider=geo.provider if geo else None,
    )
    database.add(submission)
    try:
        database.flush()
    except IntegrityError:
        database.rollback()
        existing = database.scalar(
            select(Submission).where(
                Submission.widget_id == widget.id,
                Submission.idempotency_key == idempotency_key,
            )
        )
        return {"status": "already_processed", "submission_id": existing.id}

    job = BackgroundJob(submission_id=submission.id)
    database.add(job)
    database.commit()
    background_tasks.add_task(process_confirmation_job, job.id)
    return {"status": "stored", "submission_id": submission.id, "geo_provider": submission.geo_provider}
