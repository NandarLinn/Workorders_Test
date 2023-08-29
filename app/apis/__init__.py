from fastapi import APIRouter
from apis.v1 import workorders, recommender

api_router = APIRouter()
api_router.include_router(workorders.router)
api_router.include_router(recommender.router)