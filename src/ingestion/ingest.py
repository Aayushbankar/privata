# privata/ingest_modern.py

import sys
sys.path.append('src/core')
sys.path.append('src/retrieval')
sys.path.append('src/utils')

from config import Config
from multi_modal_embedder import multi_modal_embedder
from modern_vectordb import vector_db
from enhanced_chunker import semantic_chunker
from datetime import datetime
from pathlib import Path
import hashlib
import json
from typing import Any, List, Dict


class ModernIngestionPipeline:
    """Modern ingestion pipeline with folder-aware processing"""

    def __init__(self):
        self.chunk_size = Config.ingest["chunk_size"]
        self.chunk_overlap = Config.ingest["chunk_overlap"]

    # -----------------------------
    # Step 1: Load documents
    # -----------------------------
    def load_documents(self, path: str) -> List[Dict[str, Any]]:
        """
        Load documents from enhanced crawl folder structure:
        - Each subfolder = one page
        - Prefer content.md
        - Attach structured_data.json if available
        """
        base = Path(path)
        if not base.exists():
            raise FileNotFoundError(f"Input path not found: {path}")

        document_dicts = []

        for page_dir in base.iterdir():
            if not page_dir.is_dir():
                continue

            content_file = page_dir / "content.md"
            raw_file = page_dir / "raw.html"
            structured_file = page_dir / "structured_data.json"

            text = None
            metadata = {"page": page_dir.name, "source_dir": str(page_dir)}

            if content_file.exists():
                text = content_file.read_text(encoding="utf-8", errors="ignore")
                metadata["source_file"] = str(content_file)
            elif raw_file.exists():
                text = raw_file.read_text(encoding="utf-8", errors="ignore")
                metadata["source_file"] = str(raw_file)

            if structured_file.exists():
                try:
                    metadata["structured_json"] = json.loads(
                        structured_file.read_text(encoding="utf-8")
                    )
                except Exception:
                    metadata["structured_json"] = None

            if text:
                document_dicts.append({
                    "content": text,
                    "metadata": metadata,
                })

        print(f"[INGEST] Loaded {len(document_dicts)} page-level documents")
        return document_dicts

    # -----------------------------
    # Step 2: Chunk documents
    # -----------------------------
    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Chunk documents with semantic-aware strategies"""
        # Build lightweight doc objects
        from langchain_core.documents import Document

        langchain_docs = [
            Document(page_content=doc["content"], metadata=doc["metadata"])
            for doc in documents
        ]

        # Chunk
        chunks = semantic_chunker.chunk_documents(langchain_docs)

        # Back to dicts
        chunk_dicts = []
        for chunk in chunks:
            chunk_dicts.append({
                "content": chunk.page_content,
                "metadata": chunk.metadata,
                "chunk_id": self._generate_chunk_id(chunk.page_content, chunk.metadata)
            })

        print(f"[INGEST] Created {len(chunk_dicts)} semantic chunks")
        return chunk_dicts

    # -----------------------------
    # Step 3: Deduplication
    # -----------------------------
    def deduplicate_chunks(self, chunks: List[Dict[str, Any]],
                           similarity_threshold: float = 0.95) -> List[Dict[str, Any]]:
        """Remove duplicate chunks based on content hash"""
        unique_chunks = []
        seen_hashes = set()

        for chunk in chunks:
            content_hash = hashlib.md5(chunk["content"].encode()).hexdigest()
            if content_hash not in seen_hashes:
                unique_chunks.append(chunk)
                seen_hashes.add(content_hash)
            else:
                print(f"[INGEST] Removed duplicate chunk: {chunk.get('chunk_id', 'unknown')}")

        return unique_chunks

    # -----------------------------
    # Step 4: Embedding
    # -----------------------------
    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Embed chunks with multi-modal approach"""
        embedded_chunks = multi_modal_embedder.embed_documents(chunks)
        print(f"[INGEST] Embedded {len(embedded_chunks)} chunks")
        return embedded_chunks

    # -----------------------------
    # Step 5: Storage
    # -----------------------------
    def store_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        """Store chunks in vector database"""
        store_docs = []
        for chunk in chunks:
            sanitized_metadata = self._sanitize_metadata(chunk.get("metadata", {}))
            store_docs.append({
                "content": chunk["content"],
                "embedding": chunk.get("embedding", []),
                "metadata": sanitized_metadata
            })

        vector_db.add_documents(store_docs)
        print(f"[INGEST] Stored {len(store_docs)} chunks in vector database")

    # -----------------------------
    # Orchestration
    # -----------------------------
    def run_ingestion(self, path: str, deduplicate: bool = True) -> Dict[str, Any]:
        """Run the complete modern ingestion pipeline"""
        start_time = datetime.now()
        stats = {"success": False, "start_time": start_time.isoformat(), "input_path": path}

        try:
            docs = self.load_documents(path)
            chunks = self.chunk_documents(docs)

            if deduplicate:
                chunks = self.deduplicate_chunks(chunks)

            chunks = self.embed_chunks(chunks)
            self.store_chunks(chunks)

            stats.update({
                "documents_loaded": len(docs),
                "chunks_stored": len(chunks),
                "success": True,
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "collection_stats": vector_db.get_collection_stats()
            })

            print(f"[INGEST] Completed successfully in {stats['processing_time']:.2f} sec")
        except Exception as e:
            stats.update({"error": str(e)})
            print(f"[ERROR] Ingestion failed: {e}")

        return stats

    # -----------------------------
    # Helpers
    # -----------------------------
    def _generate_chunk_id(self, content: str, metadata: Dict[str, Any]) -> str:
        source = metadata.get("source_file", "unknown")
        hash_input = f"{source}:{content[:100]}"
        return hashlib.md5(hash_input.encode()).hexdigest()

    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        clean = {}
        for k, v in metadata.items():
            if isinstance(v, (str, int, float, bool)):
                clean[k] = v
            elif v is None:
                continue
            else:
                try:
                    clean[k] = json.dumps(v)
                except Exception:
                    clean[k] = str(v)
        return clean


# Global instance
modern_pipeline = ModernIngestionPipeline()

def run_modern_ingestion(path: str):
    return modern_pipeline.run_ingestion(path)
