# privata/utils/enhanced_doc_loader.py

import re
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from langchain.schema import Document
from langchain_community.document_loaders import (
    UnstructuredPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
    UnstructuredHTMLLoader
)
import pandas as pd
from bs4 import BeautifulSoup
import html2text

class EnhancedDocumentLoader:
    """Enhanced document loader with better metadata extraction and structured content parsing"""
    
    def __init__(self):
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = False
        
    def discover_files(self, input_path: str) -> List[Path]:
        """Recursively discovers supported document files with more formats."""
        path = Path(input_path)
        if not path.exists():
            raise FileNotFoundError(f"Input path not found: {input_path}")

        extensions = {".pdf", ".txt", ".md", ".html", ".htm"}
        return [f for f in path.rglob("*") if f.suffix.lower() in extensions]
    
    def extract_metadata_from_html(self, content: str, file_path: str) -> Dict[str, Any]:
        """Extract rich metadata from HTML content"""
        soup = BeautifulSoup(content, 'html.parser')
        metadata = {
            "source_file": str(file_path),
            "file_type": "html",
            "ingestion_date": datetime.now().isoformat(),
            "title": "",
            "headings": [],
            "sections": [],
            "tables_count": 0,
            "images_count": 0,
            "links_count": 0
        }
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            metadata["title"] = title_tag.get_text().strip()
        
        # Extract headings hierarchy
        headings = []
        for level in range(1, 7):
            for heading in soup.find_all(f'h{level}'):
                headings.append({
                    "level": level,
                    "text": heading.get_text().strip(),
                    "id": heading.get('id', '')
                })
        metadata["headings"] = headings
        
        # Count tables
        metadata["tables_count"] = len(soup.find_all('table'))
        
        # Count images
        metadata["images_count"] = len(soup.find_all('img'))
        
        # Count links
        metadata["links_count"] = len(soup.find_all('a'))
        
        return metadata
    
    def extract_mission_info(self, content: str) -> Dict[str, Any]:
        """Extract mission-specific information from content"""
        mission_patterns = {
            "mission_name": r"(INSAT-3D[R]?|KALPANA-1|MeghaTropiques|SARAL-AltiKa|OCEANSAT-[23]|SCATSAT-1)",
            "dates": r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b",
            "isro_references": r"ISRO|Indian Space Research Organisation",
            "satellite_references": r"satellite|mission|payload|instrument"
        }
        
        mission_info = {}
        for key, pattern in mission_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            mission_info[key] = list(set(matches)) if matches else []
            
        return mission_info
    
    def parse_html_tables(self, content: str) -> List[Dict[str, Any]]:
        """Parse HTML tables into structured data"""
        soup = BeautifulSoup(content, 'html.parser')
        tables = []
        
        for table_idx, table in enumerate(soup.find_all('table')):
            table_data = {
                "table_index": table_idx,
                "rows": [],
                "headers": []
            }
            
            # Extract headers if present
            header_row = table.find('thead')
            if header_row:
                headers = [th.get_text().strip() for th in header_row.find_all('th')]
                table_data["headers"] = headers
            
            # Extract rows
            for row in table.find_all('tr'):
                cells = [cell.get_text().strip() for cell in row.find_all(['td', 'th'])]
                if cells:
                    table_data["rows"].append(cells)
            
            tables.append(table_data)
            
        return tables
    
    def load_file(self, path: Path) -> List[Document]:
        """Load a single file with enhanced metadata and content parsing"""
        loader_map = {
            ".pdf": UnstructuredPDFLoader,
            ".txt": TextLoader,
            ".md": UnstructuredMarkdownLoader,
            ".html": UnstructuredHTMLLoader,
            ".htm": UnstructuredHTMLLoader
        }

        loader_cls = loader_map.get(path.suffix.lower())
        if not loader_cls:
            print(f"[SKIP] Unsupported file: {path.name}")
            return []

        try:
            loader = loader_cls(str(path))
            docs = loader.load()
            
            enhanced_docs = []
            for doc in docs:
                # Extract rich metadata
                metadata = {
                    "source_file": str(path),
                    "file_extension": path.suffix.lower(),
                    "file_name": path.name,
                    "ingestion_timestamp": datetime.now().isoformat(),
                    "file_size": path.stat().st_size
                }
                
                # HTML-specific metadata extraction
                if path.suffix.lower() in ['.html', '.htm']:
                    html_metadata = self.extract_metadata_from_html(doc.page_content, str(path))
                    metadata.update(html_metadata)
                    
                    # Extract mission information
                    mission_info = self.extract_mission_info(doc.page_content)
                    metadata["mission_info"] = mission_info
                    
                    # Parse tables
                    tables = self.parse_html_tables(doc.page_content)
                    if tables:
                        metadata["parsed_tables"] = tables
                
                # Update document metadata
                doc.metadata.update(metadata)
                enhanced_docs.append(doc)
                
            return enhanced_docs
            
        except Exception as e:
            print(f"[ERROR] Failed to load {path.name}: {e}")
            return []
    
    def load_documents(self, input_path: str) -> List[Document]:
        """Load all documents from the given directory or file with enhanced processing"""
        all_docs = []
        files = [Path(input_path)] if Path(input_path).is_file() else self.discover_files(input_path)
        
        print(f"[INFO] Found {len(files)} files to process")
        
        for file in files:
            docs = self.load_file(file)
            all_docs.extend(docs)
            print(f"[INFO] Processed {file.name}: {len(docs)} documents")
            
        return all_docs

# Singleton instance for easy access
enhanced_loader = EnhancedDocumentLoader()
