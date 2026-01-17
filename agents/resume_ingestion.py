import os
from typing import Dict, Any, Tuple
import docx
from pdfminer.high_level import extract_text

class ResumeIngestionAgent:
    def __init__(self):
        pass

    def ingest(self, file_path: str) -> Dict[str, Any]:
        """
        Ingests a resume file (PDF or DOCX) and extracts text.
        
        Args:
            file_path (str): Path to the resume file.
            
        Returns:
            Dict: {
                "text": str (extracted text),
                "success": bool,
                "error": strOrNone
            }
        """
        if not os.path.exists(file_path):
            return {
                "text": "",
                "success": False,
                "error": f"File not found: {file_path}"
            }

        file_extension = os.path.splitext(file_path)[1].lower()

        try:
            if file_extension == '.pdf':
                text = self._extract_pdf(file_path)
            elif file_extension in ['.docx', '.doc']:
                text = self._extract_docx(file_path)
            else:
                return {
                    "text": "",
                    "success": False,
                    "error": f"Unsupported file format: {file_extension}"
                }
            
            if not text.strip():
                 return {
                    "text": "",
                    "success": False,
                    "error": "File content is empty or unreadable."
                }

            return {
                "text": text,
                "success": True,
                "error": None
            }

        except Exception as e:
            return {
                "text": "",
                "success": False,
                "error": str(e)
            }

    def _extract_pdf(self, file_path: str) -> str:
        return extract_text(file_path)

    def _extract_docx(self, file_path: str) -> str:
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
