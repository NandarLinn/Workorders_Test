from fastapi import FastAPI
from db import engine
from apis import api_router
import models
import os

if not os.path.exists("database"):
    os.makedirs("database")

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="Work Orders API")
app.include_router(api_router, prefix="/api/v1")