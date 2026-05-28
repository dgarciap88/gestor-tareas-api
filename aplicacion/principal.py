from contextlib import asynccontextmanager

from fastapi import FastAPI

from aplicacion.base_de_datos import Base, engine
from aplicacion.rutas import tareas


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="API de Gestión de Tareas", lifespan=lifespan)

app.include_router(tareas.router)
