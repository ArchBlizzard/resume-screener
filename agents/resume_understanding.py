from typing import Dict, Any
from utils.llm_client import LLMClient

class ResumeUnderstandingAgent:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def analyze(self, resume_text: str) -> Dict[str, Any]:
        """
        Analyzes the resume text and extracts structured data.
        """
        if not resume_text:
            return {"error": "Empty resume text provided"}

        system_prompt = """
        You are an expert Resume Parser. Your job is to extract structured information from a resume.
        Return a JSON object with the following structure:
        {
            "candidate_name": "string or null",
            "skills": ["list", "of", "skills"],
            "estimated_years_experience": float,
            "roles": [
                {"title": "string", "company": "string", "duration": "string or null", "description": "summary"}
            ],
            "education": [
                {"degree": "string", "institution": "string", "year": "string"}
            ],
            "missing_info": ["list of important missing fields if any"]
        }
        Be precise and concise. If you cannot calculate years of experience exactly, estimate conservatively based on job history.
        """

        user_prompt = f"Resume Text:\n\n{resume_text}"

        return self.llm.query(system_prompt, user_prompt, expect_json=True)
