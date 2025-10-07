from typing import List, Optional
from langchain.schema import Document
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from langchain_qdrant import QdrantVectorStore
from qdrant_client.models import Filter

from agent.models import embeddings

from api.shared.config import setting


qdrant_client = QdrantClient(url=setting.vectordb_url, api_key=setting.vectordb_api_key)
qdrant_client.delete


class VectorStoreService:
    def __init__(self, client):
        self.client: QdrantClient = client
        self._dim = 3072

    def create_customer_collection(self, company_id: str):
        """
        Create a Qdrant collection for a new customer.
        """
        collection_name = f"company_{company_id}"
        self.client.recreate_collection(
            collection_name=collection_name,
            vectors_config=rest.VectorParams(
                size=self._dim,
                distance=rest.Distance.COSINE,
            ),
        )
        return collection_name

    def get_vectorstore_for_customer(self, company_id: str) -> QdrantVectorStore:
        """
        Return a LangChain Qdrant vectorstore bound to the customer's collection.
        """
        collection_name = f"company_{company_id}"
        return QdrantVectorStore(
            client=self.client,
            collection_name=collection_name,
            embedding=embeddings,
        )

    def delete_customer_collection(self, company_id: str):
        """
        Delete a Qdrant collection for a customer.
        """
        collection_name = f"company_{company_id}"
        self.client.delete_collection(collection_name=collection_name)

    def save_documents(
        self,
        company_id: str,
        docs: list[Document],
        ids: list[str] | None = None,
    ) -> None:
        """
        Upsert a list of LangChain Documents into the customer’s collection.
        If `ids` is provided, they’ll be used as point IDs; otherwise
        Qdrant will auto‐generate UUIDs.
        """
        vs = self.get_vectorstore_for_customer(company_id)
        vs.add_documents(documents=docs, ids=ids)

    def query_similar_documents(
        self,
        company_id: str,
        query: str,
        k: int = 5,
        metadata_filter: Optional[Filter] = None,
    ) -> List[Document]:
        """
        Run a semantic similarity search over this customer's collection.
        Returns up to `k` LangChain Documents that are closest
        in embedding‐space to the given `query` string.
        You can optionally pass a Qdrant Filter to restrict results
        by metadata fields.
        """
        vs = self.get_vectorstore_for_customer(company_id)
        return vs.similarity_search(
            query,
            k=k,
            filter=metadata_filter,
        )

    def delete_by_metadata(
        self, company_id: str, metadata: dict[str, str], wait: bool = True
    ) -> None:
        """
        Delete all vectors in this customer's collection whose payload
        matches *every* key/value in the given metadata dict.
        If wait=True, the call will block until deletion is finished.
        """
        collection_name = f"company_{company_id}"
        conditions = []
        for key, value in metadata.items():
            nested_key = f"metadata.{key}"
            if isinstance(value, str):
                condition = rest.FieldCondition(
                    key=nested_key, match=rest.MatchText(text=value)
                )
            else:
                condition = rest.FieldCondition(
                    key=nested_key, match=rest.MatchValue(value=value)
                )
            conditions.append(condition)
        qdrant_filter = rest.Filter(must=conditions)
        search_result = self.client.scroll(
            collection_name=collection_name,
            scroll_filter=qdrant_filter,
            limit=10,
            with_payload=True,
        )
        if search_result[0]:
            result = self.client.delete(
                collection_name=collection_name,
                points_selector=rest.FilterSelector(filter=qdrant_filter),
                wait=wait,
            )
            return result
        else:
            return f"No points found matching metadata filter in {collection_name}"
