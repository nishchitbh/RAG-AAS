import os
import shutil
import asyncio
import functools
from fastapi import UploadFile

from api.auth.domain.entities import UserOut
from api.shared.config import setting, process_executor
from api.shared.domain.exceptions import NotFoundException
from api.document_upload.domain.schemas import FileOut, FileDelete
from api.document_upload.domain.services import UploadService, parse_pdf_task
from api.document_upload.application.abstract_upload_use_cases import IUploadUseCases
from api.notifications.infrastructure.notification_repo import (
    NotificationRepo,
    Notification,
)

from vector_store.vector_infra import VectorStoreService


class UploadUseCases(IUploadUseCases):
    def __init__(self, upload_service: UploadService, vector_db: VectorStoreService):
        self.upload_service = upload_service
        self.vector_db = vector_db

    async def upload_file(self, file: UploadFile, current_user: UserOut):
        await self.upload_service.verify_file(file)
        original_name, _ = os.path.splitext(file.filename)
        new_filename = f"{current_user.company_id}_{original_name}.pdf"
        save_path = os.path.join(setting.upload_folder, new_filename)
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return new_filename, save_path

    async def parse_and_save(self, metadata: dict):
        try:
            loop = asyncio.get_running_loop()
            file_path = metadata["file_path"]
            current_user: UserOut = metadata["current_user"]
            company_id = current_user.company_id
            parse_func = functools.partial(parse_pdf_task, file_path=file_path)
            documents, uuids = await loop.run_in_executor(process_executor, parse_func)
            self.vector_db.save_documents(
                company_id=company_id, docs=documents, ids=uuids
            )
            print("Saved successfully!")
        except Exception as e:
            filename = os.path.basename(file_path)
            company_id = filename.split("_")[0]
            notification_repo = NotificationRepo()
            notification_repo.create_notification(
                Notification(
                    company_id=company_id,
                    message=f"Document {filename} Upload Failed, Error: {e}",
                )
            )

    def get_files(self, current_user: UserOut):
        all_files = os.listdir(setting.upload_folder)
        prefix = f"{current_user.company_id}_"
        matched = [
            fname
            for fname in all_files
            if fname.startswith(prefix) and fname.lower().endswith(".pdf")
        ]
        return FileOut(files=matched)

    def delete_files(self, filename: str, current_user: UserOut):
        prefix = f"{current_user.company_id}_"
        if filename.startswith(prefix):
            file_path = os.path.join(setting.upload_folder, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
            else:
                raise NotFoundException("File not found")
            self.vector_db.delete_by_metadata(
                company_id=current_user.company_id, metadata={"file_path": filename}
            )
            return FileDelete(filename=filename)
        else:
            raise NotFoundException("File not found")
