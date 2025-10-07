from fastapi import Depends, status, File, UploadFile, BackgroundTasks

from api.document_upload.domain.schemas import FileOut, FileDelete
from api.auth.presentation.config import get_current_user, UserOut
from api.document_upload.application.upload_use_cases import UploadUseCases
from api.document_upload.presentation.config import upload_router, get_upload_use_cases


class UploadRoutes:
    def __init__(self):
        self.router = upload_router
        self.router.add_api_route(
            path="/",
            endpoint=self.upload_file,
            methods=["POST"],
            status_code=status.HTTP_201_CREATED,
        )
        self.router.add_api_route(
            path="/files",
            endpoint=self.get_files,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            response_model=FileOut,
        )
        self.router.add_api_route(
            path="/delete",
            endpoint=self.delete_file,
            methods=["DELETE"],
            status_code=status.HTTP_200_OK,
            response_model=FileDelete,
        )

    async def upload_file(
        self,
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        current_user: UserOut = get_current_user("company_admin", "super"),
        upload_use_cases: UploadUseCases = Depends(get_upload_use_cases),
    ):
        new_file_name, saved_path = await upload_use_cases.upload_file(
            file, current_user
        )
        metadata = {
            "file_path": saved_path,
            "filename": new_file_name,
            "current_user": current_user,
        }
        background_tasks.add_task(upload_use_cases.parse_and_save, metadata)
        return {"upload_status": "ok", "file_name": new_file_name}

    def get_files(
        self,
        current_user: UserOut = get_current_user("company_admin", "super"),
        upload_use_cases: UploadUseCases = Depends(get_upload_use_cases),
    ):
        return upload_use_cases.get_files(current_user=current_user)

    def delete_file(
        self,
        filename: str,
        current_user: UserOut = get_current_user("company_admin", "super"),
        upload_use_cases: UploadUseCases = Depends(get_upload_use_cases),
    ):
        return upload_use_cases.delete_files(
            filename=filename, current_user=current_user
        )
