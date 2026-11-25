import os
import re
import pymupdf as fitz  # PyMuPDF
from typing import List, Dict, Any, Optional, Tuple


class PDFService:
    @staticmethod
    def sanitize_text(text: Optional[str]) -> str:
        """
        Remove NUL (0x00) bytes rejected by PostgreSQL TEXT/VARCHAR columns while
        preserving normal Unicode characters, mathematical symbols, punctuation,
        and meaningful whitespace.
        """
        if not text:
            return ""
        return text.replace("\x00", "")

    @staticmethod
    def _parse_basic_metadata(meta: Dict[str, Any], first_page_text: str, file_name: str) -> Dict[str, Any]:
        """Extract heuristic bibliographic metadata from PDF metadata dict and page 1 text."""
        clean_first_page = PDFService.sanitize_text(first_page_text)
        title = PDFService.sanitize_text(meta.get("title") or "").strip()
        if not title or len(title) < 5 or title.lower().endswith(".pdf"):
            lines = [line.strip() for line in clean_first_page.split("\n") if line.strip()]
            candidate_title = []
            for line in lines[:4]:
                if len(line) > 3 and not re.search(r'(volume|issue|journal|proceedings|issn|isbn|arxiv)', line, re.I):
                    candidate_title.append(line)
                    if len(" ".join(candidate_title)) > 40:
                        break
            title = " ".join(candidate_title) if candidate_title else os.path.splitext(file_name)[0]

        authors = PDFService.sanitize_text(meta.get("author") or "").strip()
        if not authors:
            lines = [line.strip() for line in clean_first_page.split("\n") if line.strip()]
            for line in lines[1:6]:
                if any(x in line.lower() for x in ["university", "department", "email", "@", "institute", "laboratory"]):
                    continue
                if 5 < len(line) < 60 and not re.search(r'\d{4}', line):
                    authors = line
                    break

        abstract = ""
        abstract_match = re.search(
            r'(?i)abstract[\s:\-—]+(.*?)(?=(?:1[\.\s]|introduction|index\s+terms|keywords))',
            clean_first_page,
            re.DOTALL,
        )
        if abstract_match:
            abstract = re.sub(r'\s+', ' ', abstract_match.group(1)).strip()[:1500]
        else:
            abstract = clean_first_page[:500].strip()

        year = None
        date_str = PDFService.sanitize_text(meta.get("creationDate", "") or "")
        year_match = re.search(r'(19\d\d|20\d\d)', date_str)
        if year_match:
            year = int(year_match.group(1))
        else:
            year_matches = re.findall(r'\b(19\d\d|20[0-2]\d)\b', clean_first_page)
            if year_matches:
                year = int(year_matches[0])

        keywords = PDFService.sanitize_text(meta.get("keywords") or "").strip()
        if not keywords:
            kw_match = re.search(
                r'(?i)(?:keywords|index\s+terms)[\s:\-—]+(.*?)(?=(?:1[\.\s]|introduction|\n\n))',
                clean_first_page,
                re.DOTALL,
            )
            if kw_match:
                keywords = re.sub(r'\s+', ' ', kw_match.group(1)).strip()[:200]

        return {
            "title": PDFService.sanitize_text(title)[:500] if title else os.path.splitext(file_name)[0],
            "authors": PDFService.sanitize_text(authors)[:500] if authors else "Unknown Authors",
            "abstract": PDFService.sanitize_text(abstract) if abstract else "No abstract extracted.",
            "publication_year": year,
            "keywords": PDFService.sanitize_text(keywords)[:500] if keywords else "Research, AI, Methodology",
        }

    @staticmethod
    def extract_all(file_path: str, file_name: str) -> Tuple[List[Dict[str, Any]], int, Dict[str, Any]]:
        """
        Single-pass PDF extraction: opens the PDF once to extract all sanitized page texts,
        page count, and heuristic bibliographic metadata.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found at {file_path}")

        try:
            doc = fitz.open(file_path)
        except Exception as exc:
            raise ValueError(f"Failed to open '{file_name}' as a valid PDF: {exc}") from exc

        try:
            if doc.is_encrypted and not doc.authenticate(""):
                raise ValueError(f"PDF '{file_name}' is password-protected and cannot be read.")

            total_pages = len(doc)
            if total_pages == 0:
                raise ValueError(f"PDF '{file_name}' contains 0 pages.")

            meta = doc.metadata or {}
            first_page_raw = ""
            pages: List[Dict[str, Any]] = []

            for i, page in enumerate(doc):
                raw_text = PDFService.sanitize_text(page.get_text("text") or "")
                if i == 0:
                    first_page_raw = raw_text
                clean_text = re.sub(r'-\n\s*', '', raw_text)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                pages.append({
                    "page_number": i + 1,
                    "text": clean_text,
                })

            if not any(p["text"] for p in pages):
                raise ValueError(
                    f"No extractable text found in '{file_name}'. Scanned or image-only PDFs are not supported."
                )

            basic_meta = PDFService._parse_basic_metadata(meta, first_page_raw, file_name)
            return pages, total_pages, basic_meta
        finally:
            doc.close()

    @staticmethod
    def extract_text_and_pages(file_path: str) -> Tuple[List[Dict[str, Any]], int]:
        """
        Extracts sanitized text page by page using PyMuPDF.
        Returns:
            pages: list of dicts [{"page_number": int, "text": str}]
            total_pages: int
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found at {file_path}")

        with fitz.open(file_path) as doc:
            pages = []
            for i, page in enumerate(doc):
                text = PDFService.sanitize_text(page.get_text("text") or "")
                clean_text = re.sub(r'-\n\s*', '', text)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                pages.append({
                    "page_number": i + 1,
                    "text": clean_text,
                })
            total_pages = len(doc)
        return pages, total_pages

    @staticmethod
    def extract_basic_metadata(file_path: str, file_name: str) -> Dict[str, Any]:
        """Extracts basic metadata using PyMuPDF and rule-based heuristics."""
        with fitz.open(file_path) as doc:
            meta = doc.metadata or {}
            first_page_text = PDFService.sanitize_text(doc[0].get_text("text") if len(doc) > 0 else "")
        return PDFService._parse_basic_metadata(meta, first_page_text, file_name)

    @staticmethod
    def chunk_document(pages: List[Dict[str, Any]], chunk_size: int = 180, overlap: int = 35) -> List[Dict[str, Any]]:
        """
        Splits sanitized text into chunks preserving page number metadata.
        Default 180 words (~220 tokens) fits cleanly inside embedding token limits
        and skips empty chunks after sanitization.
        """
        chunks = []
        chunk_idx = 0

        for page in pages:
            page_num = page["page_number"]
            text = PDFService.sanitize_text(page.get("text", "")).strip()
            if not text:
                continue

            words = text.split(" ")
            i = 0
            while i < len(words):
                chunk_words = words[i : i + chunk_size]
                chunk_text = PDFService.sanitize_text(" ".join(chunk_words)).strip()
                if len(chunk_text) > 30:  # Ignore trivial/empty chunks
                    chunks.append({
                        "chunk_index": chunk_idx,
                        "page_number": page_num,
                        "content": chunk_text,
                        "token_count": len(chunk_words),
                    })
                    chunk_idx += 1
                i += max(1, chunk_size - overlap)

        return chunks
