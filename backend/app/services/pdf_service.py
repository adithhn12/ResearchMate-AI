import os
import re
import pymupdf as fitz  # PyMuPDF
from typing import List, Dict, Any, Tuple

class PDFService:
    @staticmethod
    def extract_text_and_pages(file_path: str) -> Tuple[List[Dict[str, Any]], int]:
        """
        Extracts text page by page using PyMuPDF.
        Returns:
            pages: list of dicts [{"page_number": int, "text": str}]
            total_pages: int
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found at {file_path}")

        doc = fitz.open(file_path)
        pages = []
        for i, page in enumerate(doc):
            text = page.get_text("text")
            # Clean up whitespace and hyphenation
            clean_text = re.sub(r'-\n\s*', '', text)  # join hyphenated words
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            pages.append({
                "page_number": i + 1,
                "text": clean_text
            })
        total_pages = len(doc)
        doc.close()
        return pages, total_pages

    @staticmethod
    def extract_basic_metadata(file_path: str, file_name: str) -> Dict[str, Any]:
        """
        Extracts basic metadata using PyMuPDF and rule-based heuristics.
        """
        doc = fitz.open(file_path)
        meta = doc.metadata or {}
        first_page_text = doc[0].get_text("text") if len(doc) > 0 else ""
        doc.close()

        # Heuristic title
        title = meta.get("title", "").strip()
        if not title or len(title) < 5 or title.lower().endswith(".pdf"):
            # Try to grab the first non-empty lines from page 1
            lines = [line.strip() for line in first_page_text.split("\n") if line.strip()]
            candidate_title = []
            for line in lines[:4]:
                if len(line) > 3 and not re.search(r'(volume|issue|journal|proceedings|issn|isbn|arxiv)', line, re.I):
                    candidate_title.append(line)
                    if len(" ".join(candidate_title)) > 40:
                        break
            title = " ".join(candidate_title) if candidate_title else os.path.splitext(file_name)[0]

        # Heuristic authors
        authors = meta.get("author", "").strip()
        if not authors:
            # Check for author-like lines on page 1 after title
            lines = [line.strip() for line in first_page_text.split("\n") if line.strip()]
            for line in lines[1:6]:
                if any(x in line.lower() for x in ["university", "department", "email", "@", "institute", "laboratory"]):
                    continue
                if 5 < len(line) < 60 and not re.search(r'\d{4}', line):
                    authors = line
                    break

        # Heuristic abstract
        abstract = ""
        abstract_match = re.search(r'(?i)abstract[\s:\-—]+(.*?)(?=(?:1[\.\s]|introduction|index\s+terms|keywords))', first_page_text, re.DOTALL)
        if abstract_match:
            abstract = re.sub(r'\s+', ' ', abstract_match.group(1)).strip()[:1500]
        else:
            # First 500 chars as fallback
            abstract = first_page_text[:500].strip()

        # Heuristic year
        year = None
        # Try metadata creationDate
        date_str = meta.get("creationDate", "")
        year_match = re.search(r'(19\d\d|20\d\d)', date_str)
        if year_match:
            year = int(year_match.group(1))
        else:
            year_matches = re.findall(r'\b(19\d\d|20[0-2]\d)\b', first_page_text)
            if year_matches:
                year = int(year_matches[0])

        # Heuristic keywords
        keywords = meta.get("keywords", "").strip()
        if not keywords:
            kw_match = re.search(r'(?i)(?:keywords|index\s+terms)[\s:\-—]+(.*?)(?=(?:1[\.\s]|introduction|\n\n))', first_page_text, re.DOTALL)
            if kw_match:
                keywords = re.sub(r'\s+', ' ', kw_match.group(1)).strip()[:200]

        return {
            "title": title[:500] if title else os.path.splitext(file_name)[0],
            "authors": authors[:500] if authors else "Unknown Authors",
            "abstract": abstract if abstract else "No abstract extracted.",
            "publication_year": year,
            "keywords": keywords[:500] if keywords else "Research, AI, Methodology"
        }

    @staticmethod
    def chunk_document(pages: List[Dict[str, Any]], chunk_size: int = 800, overlap: int = 150) -> List[Dict[str, Any]]:
        """
        Splits text into chunks preserving page number metadata.
        """
        chunks = []
        chunk_idx = 0

        for page in pages:
            page_num = page["page_number"]
            text = page["text"]
            if not text:
                continue

            words = text.split(" ")
            i = 0
            while i < len(words):
                chunk_words = words[i:i + chunk_size]
                chunk_text = " ".join(chunk_words).strip()
                if len(chunk_text) > 30:  # Ignore trivial chunks
                    chunks.append({
                        "chunk_index": chunk_idx,
                        "page_number": page_num,
                        "content": chunk_text,
                        "token_count": len(chunk_words)
                    })
                    chunk_idx += 1
                i += max(1, chunk_size - overlap)

        return chunks
