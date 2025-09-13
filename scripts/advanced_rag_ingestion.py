#!/usr/bin/env python3
"""
Advanced RAG-Optimized Ingestion Pipeline
=========================================

Optimized for RAG models with:
- Multi-modal content processing
- Advanced semantic chunking
- Quality-based filtering
- Context-aware embeddings
- Relationship mapping
- Performance optimization
"""

import asyncio
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedRAGIngestionPipeline:
    """Advanced ingestion pipeline optimized for RAG models"""
    
    def __init__(self, 
                 input_dir: str = "./mosdac_complete_data",
                 output_dir: str = "./chroma_db",
                 collection_name: str = "mosdac_rag_collection",
                 chunk_size: int = 800,
                 chunk_overlap: int = 150,
                 embedding_model: str = "all-MiniLM-L6-v2"):
        
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.collection_name = collection_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embedding_model = embedding_model
        
        # Initialize components
        self.embedder = SentenceTransformer(embedding_model)
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=str(self.output_dir))
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"Loaded existing collection: {collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function,
                metadata={"created": datetime.now().isoformat(), "rag_optimized": True}
            )
            logger.info(f"Created new collection: {collection_name}")
        
        # Statistics
        self.stats = {
            "documents_loaded": 0,
            "chunks_created": 0,
            "chunks_stored": 0,
            "tables_processed": 0,
            "quality_filtered": 0,
            "start_time": None,
            "end_time": None
        }
    
    def load_comprehensive_data(self) -> List[Dict[str, Any]]:
        """Load all data from comprehensive scraper output"""
        logger.info("📥 Loading comprehensive data...")
        
        if not self.input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {self.input_dir}")
        
        documents = []
        
        # Load from comprehensive index if available
        index_file = self.input_dir / "comprehensive_index.json"
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            # Process each URL from index
            for url, url_data in index_data.get("urls", {}).items():
                page_dir = Path(url_data["directory"])
                if page_dir.exists():
                    doc = self._load_single_document(page_dir, url_data)
                    if doc:
                        documents.append(doc)
        else:
            # Fallback: process all directories
            for page_dir in self.input_dir.iterdir():
                if page_dir.is_dir() and page_dir.name != "__pycache__":
                    doc = self._load_single_document(page_dir)
                    if doc:
                        documents.append(doc)
        
        self.stats["documents_loaded"] = len(documents)
        logger.info(f"✅ Loaded {len(documents)} documents")
        return documents
    
    def _load_single_document(self, page_dir: Path, url_data: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Load a single document with all its components"""
        try:
            # Load main content
            content_file = page_dir / "content.md"
            if not content_file.exists():
                return None
            
            content = content_file.read_text(encoding="utf-8", errors="ignore")
            
            # Load structured data
            structured_file = page_dir / "structured_data.json"
            structured_data = {}
            if structured_file.exists():
                with open(structured_file, 'r', encoding='utf-8') as f:
                    structured_data = json.load(f)
            
            # Load tables if available
            tables = []
            tables_file = page_dir / "tables.json"
            if tables_file.exists():
                with open(tables_file, 'r', encoding='utf-8') as f:
                    tables = json.load(f)
            
            # Create document
            doc = {
                "content": content,
                "url": structured_data.get("url", ""),
                "title": structured_data.get("title", ""),
                "metadata": structured_data.get("metadata", {}),
                "tables": tables,
                "headings": structured_data.get("headings", []),
                "quality_score": structured_data.get("quality_score", 0.0),
                "content_length": len(content),
                "source_dir": str(page_dir)
            }
            
            return doc
            
        except Exception as e:
            logger.warning(f"Failed to load document from {page_dir}: {e}")
            return None
    
    def advanced_semantic_chunking(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Advanced semantic chunking optimized for RAG"""
        logger.info("✂️ Advanced semantic chunking...")
        
        all_chunks = []
        
        for doc in documents:
            # Create base document
            langchain_doc = Document(
                page_content=doc["content"],
                metadata={
                    "url": doc["url"],
                    "title": doc["title"],
                    "source_dir": doc["source_dir"],
                    "quality_score": doc["quality_score"],
                    "content_length": doc["content_length"],
                    "tables_count": len(doc["tables"]),
                    "headings_count": len(doc["headings"])
                }
            )
            
            # Apply different chunking strategies based on content type
            chunks = self._chunk_document_intelligently(langchain_doc, doc)
            
            # Add table chunks separately
            table_chunks = self._create_table_chunks(doc)
            chunks.extend(table_chunks)
            
            all_chunks.extend(chunks)
        
        self.stats["chunks_created"] = len(all_chunks)
        logger.info(f"✅ Created {len(all_chunks)} semantic chunks")
        return all_chunks
    
    def _chunk_document_intelligently(self, doc: Document, doc_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Intelligently chunk document based on content structure"""
        chunks = []
        
        # Strategy 1: Heading-based chunking
        if doc_data["headings"]:
            heading_chunks = self._chunk_by_headings(doc, doc_data["headings"])
            chunks.extend(heading_chunks)
        
        # Strategy 2: Semantic similarity chunking
        else:
            semantic_chunks = self._chunk_by_semantic_similarity(doc)
            chunks.extend(semantic_chunks)
        
        # Strategy 3: Table-aware chunking
        if doc_data["tables"]:
            table_aware_chunks = self._chunk_around_tables(doc, doc_data["tables"])
            chunks.extend(table_aware_chunks)
        
        # Fallback: Basic recursive chunking
        if not chunks:
            base_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
            basic_chunks = base_splitter.split_documents([doc])
            chunks.extend([self._create_chunk_dict(chunk, doc_data) for chunk in basic_chunks])
        
        return chunks
    
    def _chunk_by_headings(self, doc: Document, headings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Chunk document based on heading structure"""
        chunks = []
        content = doc.page_content
        lines = content.split('\n')
        
        current_chunk = []
        current_heading = ""
        
        for line in lines:
            # Check if line is a heading
            heading_match = re.match(r'^(#+)\s+(.+)$', line.strip())
            if heading_match:
                # Save previous chunk if it has content
                if current_chunk and len('\n'.join(current_chunk)) > 50:
                    chunk_content = '\n'.join(current_chunk)
                    if len(chunk_content) <= self.chunk_size * 2:  # Allow larger chunks for sections
                        chunk_doc = Document(
                            page_content=chunk_content,
                            metadata={
                                **doc.metadata,
                                "chunk_type": "heading_based",
                                "section_heading": current_heading,
                                "chunk_size": len(chunk_content)
                            }
                        )
                        chunks.append(self._create_chunk_dict(chunk_doc, {}))
                
                # Start new chunk
                current_chunk = [line]
                current_heading = heading_match.group(2)
            else:
                current_chunk.append(line)
        
        # Add final chunk
        if current_chunk and len('\n'.join(current_chunk)) > 50:
            chunk_content = '\n'.join(current_chunk)
            chunk_doc = Document(
                page_content=chunk_content,
                metadata={
                    **doc.metadata,
                    "chunk_type": "heading_based",
                    "section_heading": current_heading,
                    "chunk_size": len(chunk_content)
                }
            )
            chunks.append(self._create_chunk_dict(chunk_doc, {}))
        
        return chunks
    
    def _chunk_by_semantic_similarity(self, doc: Document) -> List[Dict[str, Any]]:
        """Chunk document based on semantic similarity"""
        content = doc.page_content
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 3:
            return [self._create_chunk_dict(doc, {})]
        
        # Create embeddings for sentences
        sentence_embeddings = self.embedder.encode(sentences)
        
        # Group sentences by similarity
        chunks = []
        current_chunk = []
        current_chunk_size = 0
        
        for i, sentence in enumerate(sentences):
            if current_chunk_size + len(sentence) > self.chunk_size and current_chunk:
                # Create chunk from current sentences
                chunk_content = ' '.join(current_chunk)
                chunk_doc = Document(
                    page_content=chunk_content,
                    metadata={
                        **doc.metadata,
                        "chunk_type": "semantic_similarity",
                        "chunk_size": len(chunk_content)
                    }
                )
                chunks.append(self._create_chunk_dict(chunk_doc, {}))
                
                # Start new chunk
                current_chunk = [sentence]
                current_chunk_size = len(sentence)
            else:
                current_chunk.append(sentence)
                current_chunk_size += len(sentence)
        
        # Add final chunk
        if current_chunk:
            chunk_content = ' '.join(current_chunk)
            chunk_doc = Document(
                page_content=chunk_content,
                metadata={
                    **doc.metadata,
                    "chunk_type": "semantic_similarity",
                    "chunk_size": len(chunk_content)
                }
            )
            chunks.append(self._create_chunk_dict(chunk_doc, {}))
        
        return chunks
    
    def _chunk_around_tables(self, doc: Document, tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create chunks that preserve table context"""
        chunks = []
        content = doc.page_content
        
        for i, table in enumerate(tables):
            # Find table in content
            table_text = self._extract_table_text(table)
            if table_text in content:
                # Get context around table
                table_start = content.find(table_text)
                context_start = max(0, table_start - 200)
                context_end = min(len(content), table_start + len(table_text) + 200)
                
                chunk_content = content[context_start:context_end]
                
                chunk_doc = Document(
                    page_content=chunk_content,
                    metadata={
                        **doc.metadata,
                        "chunk_type": "table_context",
                        "table_index": i,
                        "table_caption": table.get("caption", ""),
                        "table_rows": table.get("row_count", 0),
                        "table_cols": table.get("col_count", 0),
                        "chunk_size": len(chunk_content)
                    }
                )
                chunks.append(self._create_chunk_dict(chunk_doc, {}))
        
        return chunks
    
    def _create_table_chunks(self, doc_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create separate chunks for tables"""
        chunks = []
        
        for i, table in enumerate(doc_data["tables"]):
            table_text = self._extract_table_text(table)
            
            chunk_doc = Document(
                page_content=table_text,
                metadata={
                    "url": doc_data["url"],
                    "title": doc_data["title"],
                    "source_dir": doc_data["source_dir"],
                    "chunk_type": "table_only",
                    "table_index": i,
                    "table_caption": table.get("caption", ""),
                    "table_rows": table.get("row_count", 0),
                    "table_cols": table.get("col_count", 0),
                    "chunk_size": len(table_text)
                }
            )
            chunks.append(self._create_chunk_dict(chunk_doc, {}))
        
        return chunks
    
    def _extract_table_text(self, table: Dict[str, Any]) -> str:
        """Extract readable text from table structure"""
        text_parts = []
        
        if table.get("caption"):
            text_parts.append(f"Table: {table['caption']}")
        
        if table.get("headers"):
            text_parts.append("Headers: " + " | ".join(table["headers"]))
        
        for row in table.get("rows", []):
            text_parts.append(" | ".join(row))
        
        return "\n".join(text_parts)
    
    def _create_chunk_dict(self, chunk_doc: Document, doc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create chunk dictionary for storage"""
        return {
            "content": chunk_doc.page_content,
            "metadata": chunk_doc.metadata,
            "chunk_id": self._generate_chunk_id(chunk_doc.page_content, chunk_doc.metadata),
            "embedding": None  # Will be filled later
        }
    
    def _generate_chunk_id(self, content: str, metadata: Dict[str, Any]) -> str:
        """Generate unique chunk ID"""
        source = metadata.get("url", "unknown")
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"{source}_{content_hash}"
    
    def quality_filtering(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter chunks based on quality metrics"""
        logger.info("🔍 Quality filtering...")
        
        filtered_chunks = []
        
        for chunk in chunks:
            # Quality criteria
            content_length = len(chunk["content"])
            quality_score = chunk["metadata"].get("quality_score", 0.0)
            chunk_type = chunk["metadata"].get("chunk_type", "unknown")
            
            # Filter criteria
            if content_length < 50:  # Too short
                continue
            
            if quality_score < 0.3 and chunk_type != "table_only":  # Low quality
                continue
            
            if content_length > self.chunk_size * 3:  # Too long
                continue
            
            # Check for meaningful content
            if self._is_meaningful_content(chunk["content"]):
                filtered_chunks.append(chunk)
        
        self.stats["quality_filtered"] = len(chunks) - len(filtered_chunks)
        logger.info(f"✅ Filtered {self.stats['quality_filtered']} low-quality chunks")
        logger.info(f"✅ Kept {len(filtered_chunks)} high-quality chunks")
        return filtered_chunks
    
    def _is_meaningful_content(self, content: str) -> bool:
        """Check if content is meaningful for RAG"""
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content.strip())
        
        # Check minimum length
        if len(content) < 50:
            return False
        
        # Check for meaningful words (not just numbers/symbols)
        words = content.split()
        meaningful_words = [w for w in words if re.match(r'^[a-zA-Z]', w)]
        
        if len(meaningful_words) < 5:
            return False
        
        # Check for common meaningless patterns
        meaningless_patterns = [
            r'^\s*$',
            r'^[0-9\s\-\.]+$',
            r'^[^\w\s]+$'
        ]
        
        for pattern in meaningless_patterns:
            if re.match(pattern, content):
                return False
        
        return True
    
    def create_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create embeddings for all chunks"""
        logger.info("🔤 Creating embeddings...")
        
        for chunk in chunks:
            content = chunk["content"]
            embedding = self.embedder.encode(content)
            chunk["embedding"] = embedding.tolist()
        
        logger.info(f"✅ Created embeddings for {len(chunks)} chunks")
        return chunks
    
    def store_in_vector_db(self, chunks: List[Dict[str, Any]]) -> None:
        """Store chunks in ChromaDB with RAG optimization"""
        logger.info("🗄️ Storing in vector database...")
        
        if not chunks:
            logger.warning("No chunks to store")
            return
        
        # Prepare data for ChromaDB
        ids = []
        embeddings = []
        metadatas = []
        documents = []
        
        for chunk in chunks:
            chunk_id = chunk["chunk_id"]
            ids.append(chunk_id)
            embeddings.append(chunk["embedding"])
            documents.append(chunk["content"])
            
            # Clean metadata for ChromaDB
            metadata = self._clean_metadata(chunk["metadata"])
            metadatas.append(metadata)
        
        # Store in ChromaDB
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )
        
        self.stats["chunks_stored"] = len(chunks)
        logger.info(f"✅ Stored {len(chunks)} chunks in vector database")
    
    def _clean_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Clean metadata for ChromaDB compatibility"""
        clean_metadata = {}
        
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                clean_metadata[key] = value
            elif value is None:
                continue
            else:
                try:
                    clean_metadata[key] = json.dumps(value)
                except:
                    clean_metadata[key] = str(value)
        
        return clean_metadata
    
    def create_relationship_mapping(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create relationship mapping for better RAG retrieval"""
        logger.info("🔗 Creating relationship mapping...")
        
        # Group chunks by source document
        source_groups = {}
        for chunk in chunks:
            source = chunk["metadata"].get("url", "unknown")
            if source not in source_groups:
                source_groups[source] = []
            source_groups[source].append(chunk)
        
        # Create relationships
        relationships = {
            "source_documents": {},
            "chunk_relationships": {},
            "content_hierarchy": {}
        }
        
        for source, source_chunks in source_groups.items():
            relationships["source_documents"][source] = {
                "chunk_count": len(source_chunks),
                "chunk_ids": [chunk["chunk_id"] for chunk in source_chunks],
                "title": source_chunks[0]["metadata"].get("title", ""),
                "quality_score": max(chunk["metadata"].get("quality_score", 0) for chunk in source_chunks)
            }
        
        return relationships
    
    def run_advanced_ingestion(self) -> Dict[str, Any]:
        """Run the complete advanced ingestion pipeline"""
        logger.info("🚀 Starting advanced RAG ingestion...")
        
        self.stats["start_time"] = datetime.now().isoformat()
        
        try:
            # Step 1: Load comprehensive data
            documents = self.load_comprehensive_data()
            if not documents:
                raise ValueError("No documents loaded")
            
            # Step 2: Advanced semantic chunking
            chunks = self.advanced_semantic_chunking(documents)
            if not chunks:
                raise ValueError("No chunks created")
            
            # Step 3: Quality filtering
            filtered_chunks = self.quality_filtering(chunks)
            if not filtered_chunks:
                raise ValueError("No chunks passed quality filtering")
            
            # Step 4: Create embeddings
            embedded_chunks = self.create_embeddings(filtered_chunks)
            
            # Step 5: Store in vector database
            self.store_in_vector_db(embedded_chunks)
            
            # Step 6: Create relationship mapping
            relationships = self.create_relationship_mapping(embedded_chunks)
            
            # Step 7: Save relationships
            relationships_file = self.output_dir / "relationships.json"
            with open(relationships_file, 'w', encoding='utf-8') as f:
                json.dump(relationships, f, indent=2, ensure_ascii=False)
            
            self.stats["end_time"] = datetime.now().isoformat()
            
            # Calculate processing time
            start_time = datetime.fromisoformat(self.stats["start_time"])
            end_time = datetime.fromisoformat(self.stats["end_time"])
            processing_time = (end_time - start_time).total_seconds()
            
            logger.info("✅ Advanced RAG ingestion completed!")
            logger.info(f"📊 Documents: {self.stats['documents_loaded']}")
            logger.info(f"📄 Chunks: {self.stats['chunks_created']}")
            logger.info(f"✅ Stored: {self.stats['chunks_stored']}")
            logger.info(f"🔍 Filtered: {self.stats['quality_filtered']}")
            logger.info(f"⏱️ Time: {processing_time:.2f} seconds")
            
            return {
                **self.stats,
                "processing_time": processing_time,
                "relationships": relationships,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"❌ Ingestion failed: {e}")
            return {
                **self.stats,
                "error": str(e),
                "success": False
            }

def main():
    """Main function"""
    pipeline = AdvancedRAGIngestionPipeline()
    result = pipeline.run_advanced_ingestion()
    
    if result["success"]:
        print("\n" + "="*60)
        print("🎉 ADVANCED RAG INGESTION COMPLETED!")
        print("="*60)
        print(f"📊 Documents: {result['documents_loaded']}")
        print(f"📄 Chunks: {result['chunks_created']}")
        print(f"✅ Stored: {result['chunks_stored']}")
        print(f"🔍 Filtered: {result['quality_filtered']}")
        print(f"⏱️ Time: {result['processing_time']:.2f} seconds")
        print("="*60)
    else:
        print(f"❌ Ingestion failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
