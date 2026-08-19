from fastapi import FastAPI

from routers import usuarios_router
from routers import auth_router
from routers import marcas_router

app = FastAPI(
    title="Perfumes Store API",
)

app.include_router(usuarios_router.usuarios_router, prefix="/api")

app.include_router(auth_router.auth_router, prefix="/api")

app.include_router(marcas_router.marcas_router, prefix="/api")