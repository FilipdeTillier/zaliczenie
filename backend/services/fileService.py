from fastapi import UploadFile, HTTPException, status, Depends
from typing import List
import os


class FilesService:
    
    async def save_files(self, files: List[UploadFile]):
        saved_files = []
        print('save files')
        for file in files:
            file_location = os.path.join('files', file.filename)
            try:
                with open(file_location, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)
                saved_files.append(file.filename)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to save file {file.filename}: {str(e)}"
                )
        return saved_files

files_service = FilesService()