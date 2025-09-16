import os
from fastapi import APIRouter

from services.qdrantService import QdrantService
from const.env_variables import  QDRANT_HOST, QDRANT_PORT

from helpers.job_helper import   read_job

qdrant_service = QdrantService(host=QDRANT_HOST, port=QDRANT_PORT)

router = APIRouter(
    prefix=""
)

@router.get("/jobs/{job_id}", tags=["Jobs"])
async def job_status(job_id: str):
    return read_job(job_id)

