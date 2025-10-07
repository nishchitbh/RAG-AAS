from abc import ABC, abstractmethod
from fastapi import UploadFile

from api.auth.domain.entities import UserOut
from api.document_upload.domain.services import UploadService

from vector_store.vector_infra import VectorStoreService


class IUploadUseCases(ABC):
    def __init__(
        self, upload_service: UploadService, vector_db: VectorStoreService
    ): ...

    @abstractmethod
    def upload_file(self, file: UploadFile, current_user: UserOut): ...

    @abstractmethod
    def parse_and_save(self, metadata: dict): ...

    @abstractmethod
    def get_files(self, current_user: UserOut): ...

    @abstractmethod
    def delete_files(self, filename: str, current_user: UserOut): ...
