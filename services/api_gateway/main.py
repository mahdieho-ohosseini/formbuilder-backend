from fastapi import FastAPI
from core.jwt_middleware import jwt_middleware
from core.rate_limit import rate_limit
from core.logging_middleware import logging_middleware

from routers.auth_proxy import router as auth_router
from routers.formbuilder_proxy import router as formbuilder_router
from routers.media_proxy import router as media_router

app = FastAPI(title="API Gateway")

# Middlewares
app.middleware("http")(logging_middleware)
app.middleware("http")(rate_limit)
app.middleware("http")(jwt_middleware)

# Routers
app.include_router(auth_router, prefix="/auth")
app.include_router(formbuilder_router, prefix="/forms")
app.include_router(media_router, prefix="/media")
