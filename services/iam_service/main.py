from fastapi import FastAPI
from routers import auth
from services.iam_service.app.core.database import engine
import models
models.base.metadata.create_all(bind=engine)
app = FastAPI(title=" auth Service" , version="1.0.0")

app.include_router(auth.router, prefix="/auth")
