import fitz  # PyMuPDF
from typing import List
import re

class PDFService:
    @staticmethod
    def extract_text(file_path: str) -> str:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            # Use block-based extraction to preserve some structure
            text += page.get_text("text") + "\n\n---PAGE_BREAK---\n\n"
        doc.close()
        return text

    @staticmethod
    def split_text(text: str, chunk_size: int = 1500, overlap: int = 300) -> List[dict]:
        """
        Splits text line-by-line to ensure structural metadata is captured precisely.
        """
        lines = text.split('\n')
        chunks = []
        
        current_unit = None
        current_part = None
        current_co = None
        
        # Regex for Structural Markers (more robust patterns)
        unit_pattern = re.compile(r'\b(unit|module|chapter)\s*[:\.-]?\s*(\d+|[ivx]+)\b', re.IGNORECASE)
        part_pattern = re.compile(r'\b(part|section)\s*[:\.-]?\s*([a-c])\b', re.IGNORECASE)
        co_pattern = re.compile(r'\b(co)\s*[:\.-]?\s*(\d+)\b', re.IGNORECASE)

        current_chunk_text = ""

        for line in lines:
            line = line.strip()
            if not line: continue
            if "---PAGE_BREAK---" in line: continue

            # Detect Header Changes
            u_match = unit_pattern.search(line)
            p_match = part_pattern.search(line)
            c_match = co_pattern.search(line)

            # If a major header change is found (Unit or Part), 
            # flush the current chunk so it's tagged with the OLD state.
            # But only if the chunk has enough text to be a real chunk.
            if (u_match or p_match) and len(current_chunk_text) > 100:
                chunks.append({
                    "text": current_chunk_text.strip(),
                    "unit": current_unit,
                    "part": current_part,
                    "co": current_co
                })
                current_chunk_text = ""

            # Update State (ONLY IF MATCHED)
            if u_match: current_unit = f"unit {u_match.group(2)}".lower()
            if p_match: current_part = f"part {p_match.group(2)}".lower()
            if c_match: current_co = f"co{c_match.group(2)}".lower()

            # Accumulate text
            current_chunk_text += line + "\n"

            # Flush if chunk size exceeded
            if len(current_chunk_text) >= chunk_size:
                chunks.append({
                    "text": current_chunk_text.strip(),
                    "unit": current_unit,
                    "part": current_part,
                    "co": current_co
                })
                current_chunk_text = ""

        if current_chunk_text.strip():
            chunks.append({
                "text": current_chunk_text.strip(),
                "unit": current_unit,
                "part": current_part,
                "co": current_co
            })
            
        return chunks
