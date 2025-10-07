import os
import threading
from pathlib import Path
from dotenv import load_dotenv
from concurrent.futures import ProcessPoolExecutor

process_executor = ProcessPoolExecutor()

load_dotenv()


class Setting:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    database_name = os.getenv("MONGO_INITDB_DATABASE")
    mongodb_connection = os.getenv("MONGODB_CONNECTION")
    auth_secret = os.getenv("AUTH_SECRET")
    access_token_expiry_time = int(os.getenv("ACCESS_TOKEN_EXPIRY_TIME"))
    algorithm = os.getenv("ALGORITHM")
    raw_upload = os.getenv("UPLOAD_FOLDER", "static/uploads").strip()
    if raw_upload.startswith(os.sep):
        raw_upload = raw_upload.lstrip(os.sep)
    upload_folder: Path = PROJECT_ROOT / raw_upload
    allowed_extensions = os.getenv("ALLOWED_EXTENSIONS").split(",")
    chunk_size = int(os.getenv("CHUNK_SIZE", 1048576))
    max_file_size = int(os.getenv("MAX_FILE_SIZE", 5))
    company_domain = os.getenv("COMPANY_DOMAIN")

    vectordb_url = os.getenv("QDRANT_URL")
    vectordb_api_key = os.getenv("QDRANT_API_KEY", None)
    vectord_prefer_grpc = os.getenv("QDRANT_PREFER_GRPC", False)


setting = Setting()


class SingletonMeta(type):
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        """Controls the instantiation of the singleton class."""
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
