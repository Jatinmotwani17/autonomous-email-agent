from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.utils import embedding_functions


class KnowledgeRetriever:
    def __init__(
        self,
        collection_name: str = "email_agent_knowledge",
        persist_dir: str = ".chroma",
    ) -> None:
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection: Collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
            metadata={"description": "Email policies and support knowledge"},
        )

    def build_index(self, docs: list[dict[str, Any]], reset: bool = True) -> int:
        if reset:
            existing_count = self.collection.count()
            if existing_count > 0:
                existing = self.collection.get(include=[])
                ids = existing.get("ids", [])
                if ids:
                    self.collection.delete(ids=ids)

        ids = [doc["id"] for doc in docs]
        texts = [doc["text"] for doc in docs]
        metadatas = [{"category": doc.get("category", "general")} for doc in docs]

        self.collection.add(ids=ids, documents=texts, metadatas=metadatas)
        return self.collection.count()

    def retrieve(self, email_text: str, top_k: int = 3) -> list[dict[str, Any]]:
        results = self.collection.query(
            query_texts=[email_text],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        docs = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        ids = results.get("ids", [[]])[0]

        retrieved: list[dict[str, Any]] = []
        for idx, doc_text in enumerate(docs):
            distance = distances[idx] if idx < len(distances) else None
            score = None if distance is None else max(0.0, 1.0 - float(distance))
            retrieved.append(
                {
                    "id": ids[idx] if idx < len(ids) else None,
                    "text": doc_text,
                    "metadata": metadatas[idx] if idx < len(metadatas) else {},
                    "distance": distance,
                    "score": score,
                }
            )

        return retrieved
