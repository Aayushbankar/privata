# privata/utils/doc_loader.py
# privata/utils/doc_loader.py

from pathlib import Path
from typing import List
from langchain.schema import Document
from langchain_community.document_loaders import (
    UnstructuredPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)



def discover_files(input_path: str) -> List[Path]:
    """Recursively discovers supported document files."""
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input path not found: {input_path}")

    extensions = {".pdf", ".txt", ".md"}
    return [f for f in path.rglob("*") if f.suffix.lower() in extensions]


def load_file(path: Path) -> List[Document]:
    """Loads a single file using the appropriate loader."""
    loader_map = {
        ".pdf": UnstructuredPDFLoader,
        ".txt": TextLoader,
        ".md": UnstructuredMarkdownLoader,
    }

    loader_cls = loader_map.get(path.suffix.lower())
    if not loader_cls:
        print(f"[SKIP] Unsupported file: {path.name}")
        return []

    try:
        loader = loader_cls(str(path))
        docs = loader.load()
        for doc in docs:
            doc.metadata["source_file"] = str(path)
        return docs
    except Exception as e:
        print(f"[ERROR] Failed to load {path.name}: {e}")
        return []


def load_documents(input_path: str) -> List[Document]:
    """Loads and returns all documents from the given directory or file."""
    all_docs = []
    files = [Path(input_path)] if Path(input_path).is_file() else discover_files(input_path)
    for file in files:
        docs = load_file(file)
        all_docs.extend(docs)
    return all_docs
