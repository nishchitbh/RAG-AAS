import os
from uuid import uuid4
from fastapi import UploadFile

from unstructured.partition.pdf import partition_pdf

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser

from agent.models import model
from agent.prompt import picture_prompt, content_rewriting_prompt

from api.shared.config import setting
from api.shared.domain.exceptions import (
    Unsupported_Media_Type,
    RequestEntityTooLargeException,
)


class UploadService:
    def __init__(self):
        self.text_input_mapping = lambda x: {
            "element": x["element"],
            "previous_context": x["previous_context"],
        }
        self.text_summarize_chain = (
            self.text_input_mapping
            | content_rewriting_prompt
            | model
            | StrOutputParser()
        )
        self.image_summarize_chain = picture_prompt | model | StrOutputParser()

    async def verify_file(self, file):
        await self.__verify_type(file)
        await self.__verify_size(file)

    async def __verify_type(self, file: UploadFile):
        if file.content_type != "application/pdf":
            raise Unsupported_Media_Type

    async def __verify_size(self, file: UploadFile):
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
        if size > 1024 * 1024 * setting.max_file_size:
            raise RequestEntityTooLargeException

    def __get_image_base64(self, chunk):
        image_b64 = []
        if "CompositeElement" in str(type(chunk)):
            chunk_els = chunk.metadata.orig_elements
            for el in chunk_els:
                if "Image" in str(type(el)):
                    image_b64.append(el.metadata.image_base64)
        return image_b64

    def parse_pdf(self, file_path):
        chunks = partition_pdf(
            filename=file_path,
            infer_table_structure=True,
            strategy="hi_res",
            extract_image_block_types=["Image"],
            extract_image_block_to_payload=True,
            chunking_strategy="by_title",
            max_characters=10000,
            combine_text_under_n_chars=2000,
            new_after_n_chars=6000,
        )
        previous = ["Beginning of the file"]

        text_summaries = []
        for chunk in chunks:
            text_summary = self.text_summarize_chain.invoke(
                {"element": chunk, "previous_context": previous[-1]}
            )
            images = self.__get_image_base64(chunk)
            image_summaries = self.image_summarize_chain.batch(images)
            text_summary = (
                text_summary + "Image Summaries: " + " ".join(image_summaries)
            )
            text_summaries.append(text_summary)
            previous.append(text_summary)
        filename = os.path.basename(file_path)
        documents = [
            Document(page_content=text_summary, metadata={"file_path": filename})
            for text_summary in text_summaries
        ]
        uuids = [str(uuid4()) for _ in range(len(documents))]
        return documents, uuids


def parse_pdf_task(file_path: str) -> tuple[list, list]:
    """
    Top‐level function so it can be pickled.
    Recreate the UploadService here so no problematic lambdas are carried over.
    """

    service = UploadService()
    documents, uuids = service.parse_pdf(file_path=file_path)
    return documents, uuids
