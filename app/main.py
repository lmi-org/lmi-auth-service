import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, users
from app.config import settings
from app.core.middleware import log_requests
from app.database import Base, engine

logging.basicConfig(
    filename=settings.log_file,
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
)



@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.project_name,
    debug=settings.debug,
    lifespan=lifespan,
)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(log_requests)

app.include_router(auth.router)
app.include_router(users.router)


@app.get("/health")
def health():
    return {"status": "ok"}
