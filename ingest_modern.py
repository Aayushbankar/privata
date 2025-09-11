# privata/ingest_modern.py

from config import Config
from utils.enhanced_doc_loader import enhanced_loader
from utils.enhanced_chunker import semantic_chunker
from utils.structured_extractor import structured_extractor
from retriever.multi_modal_embedder import multi_modal_embedder
from retriever.modern_vectordb import vector_db
import json
from datetime import datetime
import hashlib

class ModernIngestionPipeline:
    """Modern ingestion pipeline with enhanced processing and structured data extraction"""
    
    def __init__(self):
        self.chunk_size = Config.ingest["chunk_size"]
        self.chunk_overlap = Config.ingest["chunk_overlap"]
        
    def load_documents(self, path: str) -> List[Dict[str, Any]]:
        """Load documents with enhanced metadata extraction"""
        print(f"[INGEST] Loading documents from: {path}")
        
        # Use enhanced document loader
        docs = enhanced_loader.load_documents(path)
        
        # Convert to dict format for processing
        document_dicts = []
        for doc in docs:
            doc_dict = {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "raw_document": doc  # Keep original for reference
            }
            document_dicts.append(doc_dict)
        
        print(f"[INGEST] Loaded {len(document_dicts)} documents")
        return document_dicts
    
    def extract_structured_data(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract structured data from documents"""
        enhanced_docs = []
        
        for doc in documents:
            try:
                # Extract structured data
                structured_data = structured_extractor.extract_structured_data(
                    doc["content"], doc["metadata"]
                )
                
                # Update document with structured data
                doc["structured_data"] = structured_data
                doc["metadata"]["structured_extracted"] = True
                doc["metadata"]["extraction_timestamp"] = datetime.now().isoformat()
                
                enhanced_docs.append(doc)
                
            except Exception as e:
                print(f"[ERROR] Structured data extraction failed for document: {e}")
                # Keep document without structured data
                doc["metadata"]["structured_extracted"] = False
                enhanced_docs.append(doc)
        
        print(f"[INGEST] Structured data extracted for {len(enhanced_docs)} documents")
        return enhanced_docs
    
    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Chunk documents with semantic-aware strategies"""
        # Convert to Document objects for chunking
        langchain_docs = []
        for doc in documents:
            langchain_doc = doc["raw_document"]
            langchain_docs.append(langchain_doc)
        
        # Use semantic chunker
        chunks = semantic_chunker.chunk_documents(langchain_docs)
        
        # Convert back to dict format
        chunk_dicts = []
        for chunk in chunks:
            chunk_dict = {
                "content": chunk.page_content,
                "metadata": chunk.metadata,
                "chunk_id": self._generate_chunk_id(chunk.page_content, chunk.metadata)
            }
            chunk_dicts.append(chunk_dict)
        
        print(f"[INGEST] Created {len(chunk_dicts)} semantic chunks")
        return chunk_dicts
    
    def _generate_chunk_id(self, content: str, metadata: Dict[str, Any]) -> str:
        """Generate unique ID for chunk based on content and metadata"""
        source_file = metadata.get("source_file", "unknown")
        chunk_index = metadata.get("chunk_index", 0)
        
        # Create hash based on content and source
        hash_input = f"{source_file}:{chunk_index}:{content[:100]}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Embed chunks with multi-modal approach"""
        embedded_chunks = multi_modal_embedder.embed_documents(chunks)
        print(f"[INGEST] Embedded {len(embedded_chunks)} chunks")
        return embedded_chunks
    
    def store_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        """Store chunks in vector database"""
        # Prepare documents for storage
        store_docs = []
        for chunk in chunks:
            store_docs.append({
                "content": chunk["content"],
                "embedding": chunk.get("embedding", []),
                "metadata": chunk.get("metadata", {})
            })
        
        # Store in vector database
        vector_db.add_documents(store_docs)
        print(f"[INGEST] Stored {len(store_docs)} chunks in vector database")
    
    def deduplicate_chunks(self, chunks: List[Dict[str, Any]], 
                         similarity_threshold: float = 0.95) -> List[Dict[str, Any]]:
        """Remove duplicate chunks based on content similarity"""
        unique_chunks = []
        seen_hashes = set()
        
        for chunk in chunks:
            # Create content hash for deduplication
            content_hash = hashlib.md5(chunk["content"].encode()).hexdigest()
            
            if content_hash not in seen_hashes:
                unique_chunks.append(chunk)
                seen_hashes.add(content_hash)
            else:
                print(f"[INGEST] Removed duplicate chunk: {chunk.get('chunk_id', 'unknown')}")
        
        duplicates_removed = len(chunks) - len(unique_chunks)
        if duplicates_removed > 0:
            print(f"[INGEST] Removed {duplicates_removed} duplicate chunks")
        
        return unique_chunks
    
    def run_ingestion(self, path: str, deduplicate: bool = True) -> Dict[str, Any]:
        """Run the complete modern ingestion pipeline"""
        start_time = datetime.now()
        stats = {
            "start_time": start_time.isoformat(),
            "input_path": path,
            "documents_loaded": 0,
            "chunks_created": 0,
            "chunks_stored": 0,
            "duplicates_removed": 0,
            "processing_time": 0,
            "success": False
        }
        
        try:
            # Step 1: Load documents
            documents = self.load_documents(path)
            stats["documents_loaded"] = len(documents)
            
            # Step 2: Extract structured data
            documents = self.extract_structured_data(documents)
            
            # Step 3: Chunk documents
            chunks = self.chunk_documents(documents)
            stats["chunks_created"] = len(chunks)
            
            # Step 4: Deduplicate (optional)
            if deduplicate:
                original_count = len(chunks)
                chunks = self.deduplicate_chunks(chunks)
                stats["duplicates_removed"] = original_count - len(chunks)
            
            # Step 5: Embed chunks
            chunks = self.embed_chunks(chunks)
            
            # Step 6: Store chunks
            self.store_chunks(chunks)
            stats["chunks_stored"] = len(chunks)
            
            # Final stats
            end_time = datetime.now()
            stats["end_time"] = end_time.isoformat()
            stats["processing_time"] = (end_time - start_time).total_seconds()
            stats["success"] = True
            
            # Add collection stats
            collection_stats = vector_db.get_collection_stats()
            stats["collection_stats"] = collection_stats
            
            print(f"[INGEST] Ingestion completed successfully in {stats['processing_time']:.2f} seconds")
            print(f"[INGEST] Collection stats: {json.dumps(collection_stats, indent=2)}")
            
        except Exception as e:
            end_time = datetime.now()
            stats["end_time"] = end_time.isoformat()
            stats["processing_time"] = (end_time - start_time).total_seconds()
            stats["error"] = str(e)
            stats["success"] = False
            
            print(f"[ERROR] Ingestion failed: {e}")
        
        return stats
    
    def incremental_update(self, path: str) -> Dict[str, Any]:
        """Incremental update - detect and process only new/changed files"""
        # This would implement file change detection and partial processing
        # For now, fall back to full ingestion
        print("[INGEST] Incremental update not implemented yet, running full ingestion")
        return self.run_ingestion(path)

# Global instance for easy access
modern_pipeline = ModernIngestionPipeline()

def run_modern_ingestion(path: str):
    """Run the modern ingestion pipeline"""
    return modern_pipeline.run_ingestion(path)

def incremental_update(path: str):
    """Run incremental update"""
    return modern_pipeline.incremental_update(path)
