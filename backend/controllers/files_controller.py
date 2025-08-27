import os
from fastapi import HTTPException, APIRouter
from services.qdrantService import QdrantService
import os
import uuid
import mimetypes
from typing import List, Dict, Any
from fastapi import HTTPException, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse
from services.qdrantService import QdrantService
from helpers.files_helper import list_saved_files, sha256_stream_to_tmp, storage_path_for_checksum
from helpers.job_helper import  write_job, process_job
from const.env_variables import  QDRANT_HOST, QDRANT_PORT, UPLOAD_DIR

qdrant_service = QdrantService(host=QDRANT_HOST, port=QDRANT_PORT)

router = APIRouter(
    prefix="",
    tags=[""]
)

@router.post("/upload")
async def upload(files: List[UploadFile], background_tasks: BackgroundTasks) -> Dict[str, Any]:
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    job_id = str(uuid.uuid4())
    saved_items = []
    storage_keys_for_job = []

    for f in files:
        checksum, tmp_path, size_bytes = sha256_stream_to_tmp(f.file)
        rel_path = storage_path_for_checksum(checksum, f.filename)
        abs_path = os.path.join(UPLOAD_DIR, rel_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)

        if os.path.exists(abs_path):
            try:
                os.remove(tmp_path)
            except FileNotFoundError:
                pass
            dedup = True
        else:
            os.replace(tmp_path, abs_path)
            dedup = False

        ctype, _ = mimetypes.guess_type(f.filename)
        saved_items.append({
            "filename": f.filename,
            "checksum_sha256": checksum,
            "size_bytes": size_bytes,
            "storage_key": rel_path,
            "content_type": ctype or "application/octet-stream",
            "deduplicated": dedup,
            "download_url": f"/files/{checksum}/{f.filename}/download",
        })
        storage_keys_for_job.append(rel_path)

    write_job(job_id, {"job_id": job_id, "status": "queued", "items": storage_keys_for_job})
    background_tasks.add_task(process_job, job_id, storage_keys_for_job)

    return {"job_id": job_id, "status": "queued", "count": len(saved_items), "items": saved_items}


@router.get("/files")
async def files_list():
    items = list_saved_files()
    return {"count": len(items), "items": items}

@router.get("/files/{checksum}/{filename}/download")
async def download_file(checksum: str, filename: str):
    rel_path = storage_path_for_checksum(checksum, filename)
    abs_path = os.path.join(UPLOAD_DIR, rel_path)
    if not os.path.exists(abs_path):
        raise HTTPException(status_code=404, detail="File not found")
    ctype, _ = mimetypes.guess_type(filename)
    return FileResponse(abs_path, media_type=ctype or "application/octet-stream", filename=filename)
