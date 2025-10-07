from fastapi import APIRouter

from api.document_upload.domain.services import UploadService
from api.document_upload.application.upload_use_cases import UploadUseCases

from vector_store.vector_infra import qdrant_client, VectorStoreService

upload_router = APIRouter(prefix="/upload", tags=["PDF Upload"])


def get_upload_use_cases():
    uplaod_service = UploadService()
    return UploadUseCases(
        upload_service=uplaod_service,
        vector_db=VectorStoreService(client=qdrant_client),
    )
