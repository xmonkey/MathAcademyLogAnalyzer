"""PDF parsing functionality using pdfplumber."""

import pdfplumber
from typing import List, Dict, Any, Optional
from pathlib import Path


class PDFParser:
    """A class to parse PDF files using pdfplumber."""

    def __init__(self, pdf_path: str):
        """Initialize the PDF parser with a file path."""
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    def extract_text(self) -> str:
        """Extract all text from the PDF."""
        text_content = []
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
        
        return "\n".join(text_content)

    def extract_text_by_page(self) -> List[str]:
        """Extract text from each page separately."""
        pages_text = []
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                pages_text.append(text or "")
        
        return pages_text

    def extract_tables(self) -> List[List[List[str]]]:
        """Extract all tables from the PDF."""
        all_tables = []
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                all_tables.extend(tables)
        
        return all_tables

    def extract_tables_by_page(self) -> Dict[int, List[List[str]]]:
        """Extract tables from each page separately."""
        tables_by_page = {}
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                if tables:
                    tables_by_page[page_num + 1] = tables
        
        return tables_by_page

    def get_metadata(self) -> Dict[str, Any]:
        """Extract metadata from the PDF."""
        with pdfplumber.open(self.pdf_path) as pdf:
            metadata = pdf.metadata
        
        return metadata or {}

    def get_page_count(self) -> int:
        """Get the total number of pages in the PDF."""
        with pdfplumber.open(self.pdf_path) as pdf:
            return len(pdf.pages)

    def extract_text_with_positions(self) -> List[Dict[str, Any]]:
        """Extract text with position information."""
        text_with_positions = []
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                chars = page.chars
                if chars:
                    text_with_positions.extend([
                        {
                            "page": page_num + 1,
                            "text": char["text"],
                            "x0": char["x0"],
                            "top": char["top"],
                            "x1": char["x1"],
                            "bottom": char["bottom"],
                            "size": char["size"],
                            "font": char.get("fontname", ""),
                        }
                        for char in chars
                    ])
        
        return text_with_positions

    def search_text(self, search_term: str) -> List[Dict[str, Any]]:
        """Search for specific text in the PDF."""
        results = []
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text and search_term.lower() in text.lower():
                    results.append({
                        "page": page_num + 1,
                        "found": True,
                        "context": self._get_context(text, search_term)
                    })
        
        return results

    def _get_context(self, text: str, search_term: str, context_chars: int = 100) -> str:
        """Get context around the search term."""
        search_lower = text.lower()
        term_lower = search_term.lower()
        index = search_lower.find(term_lower)
        
        if index == -1:
            return ""
        
        start = max(0, index - context_chars)
        end = min(len(text), index + len(search_term) + context_chars)
        
        context = text[start:end]
        return f"...{context}..."