import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models import BackgroundJob, Submission


logger = logging.getLogger("widget-platform.jobs")


def send_confirmation(submission: Submission) -> None:
    if settings.side_effect_force_failure:
        raise RuntimeError("Forced confirmation failure")
    logger.info("Confirmation sent for submission_id=%s email=%s", submission.id, submission.email)


def process_confirmation_job(job_id: int) -> None:
    database: Session = SessionLocal()
    try:
        job = database.get(BackgroundJob, job_id)
        if job is None or job.status == "completed":
            return
        submission = database.get(Submission, job.submission_id)
        if submission is None:
            job.status = "failed"
            job.last_error = "Submission missing"
            database.commit()
            return
        for attempt in range(job.attempts + 1, settings.background_job_max_attempts + 1):
            job.attempts = attempt
            try:
                send_confirmation(submission)
                job.status = "completed"
                job.completed_at = datetime.now(timezone.utc)
                job.last_error = None
                database.commit()
                return
            except Exception as error:
                job.last_error = str(error)
                database.commit()
        job.status = "failed"
        database.commit()
        logger.error("BACKGROUND_JOB_FAILURE job_id=%s error=%s", job.id, job.last_error)
    finally:
        database.close()
