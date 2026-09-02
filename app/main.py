from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, engine
from app.routers import auth_routes, dashboard_routes, submission_routes, widget_routes


@asynccontextmanager
async def lifespan(application: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Embeddable Widget & Lead-Capture Platform",
    description="Tenant-isolated widget delivery and resilient public lead capture.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Idempotency-Key"],
)


@app.middleware("http")
async def reject_oversized_bodies(request: Request, call_next):
    if request.method in {"POST", "PUT", "PATCH"}:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > settings.max_body_bytes:
            return JSONResponse(status_code=413, content={"error": "Request body too large"})
    response = await call_next(request)
    if request.url.path == "/assets/widget.v1.js":
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    return response


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, error: RequestValidationError):
    return JSONResponse(status_code=422, content={"error": "Validation failed", "details": error.errors()})


@app.get("/health", tags=["System"])
def health():
    return {"status": "healthy"}


app.include_router(auth_routes.router)
app.include_router(widget_routes.router)
app.include_router(submission_routes.router)
app.include_router(dashboard_routes.router)
app.mount("/assets", StaticFiles(directory="app/static"), name="assets")
