import os
import mimetypes
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid
import hashlib
from const.env_variables import UPLOAD_DIR, JOBS_DIR, TMP_DIR

os.makedirs(TMP_DIR, exist_ok=True)

def _find_job_for_storage_key(storage_key: str) -> Optional[Dict[str, str]]:
    """Find job metadata for a given storage_key by scanning job files."""
    try:
        if not os.path.exists(JOBS_DIR):
            return None
        for fname in os.listdir(JOBS_DIR):
            if not fname.endswith(".json"):
                continue
            job_path = os.path.join(JOBS_DIR, fname)
            try:
                with open(job_path, "r", encoding="utf-8") as jf:
                    data = jf.read()
                import json as _json
                payload = _json.loads(data)
            except Exception:
                continue
            items = payload.get("items", []) or []
            if storage_key in items:
                return {"job_id": payload.get("job_id"), "job_status": payload.get("status")}
        return None
    except Exception:
        return None


def list_saved_files() -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for root, dirs, files in os.walk(UPLOAD_DIR):
        rel_root = os.path.relpath(root, UPLOAD_DIR)
        parts = rel_root.split(os.sep)
        if parts[0] in {".", "tmp", ".jobs"}:
            continue
        for fname in files:
            rel_path = os.path.join(rel_root, fname) if rel_root != "." else fname
            path_parts = rel_path.split(os.sep)
            if len(path_parts) < 4:
                continue
            a, b, checksum, filename = path_parts[-4:]
            if a != checksum[:2] or b != checksum[2:4] or filename != fname:
                continue
            abs_path = os.path.join(UPLOAD_DIR, rel_path)
            try:
                size = os.path.getsize(abs_path)
                mtime = os.path.getmtime(abs_path)
            except FileNotFoundError:
                continue
            ctype, _ = mimetypes.guess_type(filename)
            item: Dict[str, Any] = {
                "filename": filename,
                "checksum_sha256": checksum,
                "size_bytes": size,
                "storage_key": os.path.join(a, b, checksum, filename),
                "content_type": ctype or "application/octet-stream",
                "created_at": datetime.utcfromtimestamp(mtime).isoformat(),
                "download_url": f"/files/{checksum}/{filename}/download",
            }
            job_info = _find_job_for_storage_key(item["storage_key"])
            if job_info:
                item.update(job_info)
            items.append(item)
    items.sort(key=lambda x: x["created_at"], reverse=True)
    return items

def sha256_stream_to_tmp(src_fobj) -> tuple[str, str, int]:
    """Zapisuje stream do pliku tymczasowego, licząc SHA-256 i rozmiar."""
    os.makedirs(TMP_DIR, exist_ok=True)
    tmp_path = os.path.join(TMP_DIR, f"{uuid.uuid4().hex}.upload")
    h = hashlib.sha256()
    total = 0
    with open(tmp_path, "wb") as out:
        while True:
            chunk = src_fobj.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
            out.write(chunk)
            total += len(chunk)
    return h.hexdigest(), tmp_path, total


def storage_path_for_checksum(checksum: str, filename: str) -> str:
    return os.path.join(checksum[:2], checksum[2:4], checksum, filename)

def remove_file_by_checksum_and_filename(checksum: str, filename: str) -> bool:
    """
    Removes a file from storage given its checksum and filename.

    Args:
        checksum (str): SHA-256 checksum of the file.
        filename (str): Name of the file.

    Returns:
        bool: True if the file was removed, False if it did not exist.
    """
    rel_path = storage_path_for_checksum(checksum, filename)
    abs_path = os.path.join(UPLOAD_DIR, rel_path)
    try:
        os.remove(abs_path)
        return True
    except FileNotFoundError:
        return False
    except Exception as e:
        return False
