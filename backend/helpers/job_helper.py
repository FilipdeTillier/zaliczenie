import os
import json
from datetime import datetime

from typing import List, Dict, Any
from helpers.chunk_helper import chunk_file
from services.qdrantService import qdrant_service
from fastapi import HTTPException

from const.env_variables import UPLOAD_DIR, JOBS_DIR


def job_file(job_id: str) -> str:
    return os.path.join(JOBS_DIR, f"{job_id}.json")


def write_job(job_id: str, payload: Dict[str, Any]) -> None:
    jf = job_file(job_id)
    os.makedirs(os.path.dirname(jf), exist_ok=True)
    payload["updated_at"] = datetime.utcnow().isoformat()
    tmp_path = jf + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, jf)


def read_job(job_id: str) -> Dict[str, Any]:
    path = job_file(job_id)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Job not found")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def process_job(job_id: str, storage_keys: List[str]) -> None:
    write_job(job_id, {"job_id": job_id, "status": "processing", "items": storage_keys})
    try:
        total_chunks = 0
        total_upserted = 0
        per_file = []

        for key in storage_keys:
            abs_path = os.path.join(UPLOAD_DIR, key)
            chunks_with_metadata = chunk_file(abs_path)
            chunks = [chunk["text"] for chunk in chunks_with_metadata]
            metadata_list = [chunk["metadata"] for chunk in chunks_with_metadata]
            
            upserted = qdrant_service.upsert_chunks_to_qdrant(key, chunks, metadata_list, job_id=job_id, use_openai=True)
            total_chunks += len(chunks)
            total_upserted += upserted
            per_file.append({"storage_key": key, "chunks": len(chunks), "upserted": upserted})

        write_job(job_id, {
            "job_id": job_id,
            "status": "completed",
            "items": storage_keys,
            "summary": {"total_chunks": total_chunks, "total_upserted": total_upserted, "per_file": per_file},
        })
    except Exception as e:
        write_job(job_id, {"job_id": job_id, "status": "failed", "error": str(e), "items": storage_keys})