import time
from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from . import crud
from .auth import current_user, issue_token
from .database import SessionLocal, get_db
from .models import Device, DeviceRow, Reading, ReadingInput, ToggleResult


REQUESTS = Counter("smart_home_http_requests", "HTTP requests", ["method", "route", "status"])
DURATION = Histogram("smart_home_http_duration_seconds", "HTTP request duration", ["method", "route"])


@asynccontextmanager
async def lifespan(app):
    crud.initialize_database()
    yield


app = FastAPI(title="API умного дома", lifespan=lifespan)
router = APIRouter()
router.post("/token")(issue_token)


@app.middleware("http")
async def measure_requests(request, call_next):
    start = time.perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        route = getattr(request.scope.get("route"), "path", "unmatched")
        if route not in {"/metrics", "/health", "/api/health"}:
            method = request.method
            REQUESTS.labels(method, route, str(status)).inc()
            DURATION.labels(method, route).observe(time.perf_counter() - start)


@router.get("/health")
def health():
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
    except OperationalError as error:
        raise HTTPException(503, "PostgreSQL недоступен") from error
    return {"status": "ok"}


@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(generate_latest(), headers={"Content-Type": CONTENT_TYPE_LATEST})


@router.get("/devices", response_model=list[Device], dependencies=[Depends(current_user)])
def devices(session: Session = Depends(get_db)):
    return crud.list_devices(session)


@router.post("/devices/{device_id}/toggle", response_model=ToggleResult, dependencies=[Depends(current_user)])
def toggle(device_id: int, session: Session = Depends(get_db)):
    device = crud.toggle_device(session, device_id)
    if device is None:
        raise HTTPException(404, "Устройство не найдено")
    return {"device": device}


def require_device(device_id, session):
    if session.get(DeviceRow, device_id) is None:
        raise HTTPException(404, "Устройство не найдено")


@router.post("/devices/{device_id}/readings", response_model=Reading, status_code=201,
             dependencies=[Depends(current_user)])
def add_reading(device_id: int, reading: ReadingInput, session: Session = Depends(get_db)):
    require_device(device_id, session)
    return crud.add_reading(session, device_id, reading.value)


@router.get("/devices/{device_id}/readings", response_model=list[Reading],
            dependencies=[Depends(current_user)])
def readings(device_id: int, session: Session = Depends(get_db)):
    require_device(device_id, session)
    return crud.list_readings(session, device_id)


app.include_router(router)
app.include_router(router, prefix="/api", include_in_schema=False)
