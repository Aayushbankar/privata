# privata/utils/enhanced_chunker.py

from typing import List, Dict, Any
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import re
from bs4 import BeautifulSoup
from typing import Any , List, Dict

class SemanticChunker:
    """Enhanced chunking strategy that respects document structure and semantics"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.base_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    
    def chunk_by_headings(self, doc: Document) -> List[Document]:
        """Chunk document based on HTML heading structure"""
        if not doc.metadata.get('headings'):
            return [doc]  # Fallback to single chunk
        
        content = doc.page_content
        headings = doc.metadata['headings']
        
        if not headings:
            return [doc]
        
        # Create chunks based on heading boundaries
        chunks = []
        current_chunk_content = ""
        current_heading_level = 0
        current_section = ""
        
        # Simple approach: split by major headings (h1, h2)
        lines = content.split('\n')
        current_section_lines = []
        
        for line in lines:
            # Check if line contains a heading pattern
            heading_match = re.match(r'^(#+)\s+(.+)$', line.strip())
            if heading_match:
                # If we have accumulated content, create a chunk
                if current_section_lines:
                    chunk_content = '\n'.join(current_section_lines)
                    if chunk_content.strip():
                        chunk_doc = Document(
                            page_content=chunk_content,
                            metadata=doc.metadata.copy()
                        )
                        chunk_doc.metadata['section_title'] = current_section
                        chunks.append(chunk_doc)
                
                # Start new section
                current_section = heading_match.group(2)
                current_section_lines = [line]
            else:
                current_section_lines.append(line)
        
        # Add the last section
        if current_section_lines:
            chunk_content = '\n'.join(current_section_lines)
            if chunk_content.strip():
                chunk_doc = Document(
                    page_content=chunk_content,
                    metadata=doc.metadata.copy()
                )
                chunk_doc.metadata['section_title'] = current_section
                chunks.append(chunk_doc)
        
        return chunks if chunks else [doc]
    
    def chunk_by_semantic_units(self, doc: Document) -> List[Document]:
        """Chunk document into semantic units (paragraphs, lists, tables)"""
        content = doc.page_content
        
        # Split by double newlines (paragraphs)
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = []
        current_length = 0
        
        for paragraph in paragraphs:
            para_length = len(paragraph)
            
            # If adding this paragraph would exceed chunk size, finalize current chunk
            if current_length + para_length > self.chunk_size and current_chunk:
                chunk_content = '\n\n'.join(current_chunk)
                chunk_doc = Document(
                    page_content=chunk_content,
                    metadata=doc.metadata.copy()
                )
                chunks.append(chunk_doc)
                current_chunk = [paragraph]
                current_length = para_length
            else:
                current_chunk.append(paragraph)
                current_length += para_length + 2  # +2 for newlines
        
        # Add the last chunk
        if current_chunk:
            chunk_content = '\n\n'.join(current_chunk)
            chunk_doc = Document(
                page_content=chunk_content,
                metadata=doc.metadata.copy()
            )
            chunks.append(chunk_doc)
        
        return chunks
    
    def preserve_table_integrity(self, doc: Document) -> List[Document]:
        """Ensure tables are not split across chunks"""
        content = doc.page_content
        
        # Simple table detection (look for pipe-separated or grid patterns)
        table_pattern = r'(\|.*\|[\n\r]+)+'
        tables = re.findall(table_pattern, content)
        
        if not tables:
            return [doc]
        
        # Split content around tables
        chunks = []
        remaining_content = content
        
        for table in tables:
            parts = remaining_content.split(table, 1)
            if len(parts) == 2:
                # Add content before table
                if parts[0].strip():
                    chunks.append(Document(
                        page_content=parts[0].strip(),
                        metadata=doc.metadata.copy()
                    ))
                
                # Add table as separate chunk
                chunks.append(Document(
                    page_content=table.strip(),
                    metadata=doc.metadata.copy()
                ))
                
                remaining_content = parts[1]
            else:
                remaining_content = parts[0]
        
        # Add remaining content
        if remaining_content.strip():
            chunks.append(Document(
                page_content=remaining_content.strip(),
                metadata=doc.metadata.copy()
            ))
        
        return chunks
    
    def chunk_document(self, doc: Document) -> List[Document]:
        """Main chunking method with multiple strategies"""
        
        # Strategy 1: If HTML with headings, chunk by headings
        if doc.metadata.get('headings'):
            heading_chunks = self.chunk_by_headings(doc)
            if len(heading_chunks) > 1:
                return heading_chunks
        
        # Strategy 2: Preserve table integrity
        table_chunks = self.preserve_table_integrity(doc)
        if len(table_chunks) > 1:
            return table_chunks
        
        # Strategy 3: Chunk by semantic units
        semantic_chunks = self.chunk_by_semantic_units(doc)
        if len(semantic_chunks) > 1:
            return semantic_chunks
        
        # Strategy 4: Fallback to base splitter for large content
        if len(doc.page_content) > self.chunk_size * 1.5:
            return self.base_splitter.split_documents([doc])
        
        # Default: return single chunk
        return [doc]
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Chunk multiple documents with enhanced strategies"""
        all_chunks = []
        
        for doc in documents:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)
            
            # Add chunk metadata
            for i, chunk in enumerate(chunks):
                chunk.metadata['chunk_index'] = i
                chunk.metadata['total_chunks'] = len(chunks)
                chunk.metadata['chunking_strategy'] = self.__class__.__name__
        
        print(f"[INFO] Chunked {len(documents)} docs into {len(all_chunks)} semantic chunks")
        return all_chunks

# Global instance for easy access
semantic_chunker = SemanticChunker()
