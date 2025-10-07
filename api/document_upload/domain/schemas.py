from typing import List
from pydantic import BaseModel


class FileOut(BaseModel):
    files: List[str]


class FileDelete(BaseModel):
    filename: str
    message: str = "The file has been deleted successfully!"
