from typing import Dict, Any
from utils.llm_client import LLMClient

class JobUnderstandingAgent:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def analyze(self, job_description: str) -> Dict[str, Any]:
        """
        Analyzes the job description and extracts structured requirements.
        """
        if not job_description:
            return {"error": "Empty job description provided"}

        system_prompt = """
        You are an expert HR Analyst. Analyze the following Job Description.
        Return a JSON object with the following structure:
        {
            "job_title": "string",
            "required_skills": ["list", "of", "must-have", "skills"],
            "preferred_skills": ["list", "of", "nice-to-have", "skills"],
            "minimum_experience_years": float,
            "education_requirements": "string or null",
            "role_level": "Entry | Mid | Senior | Lead | Executive"
        }
        Extract skills precisely. If minimum experience isn't explicitly stated, estimate based on the role level (e.g. Senior ~ 5+ years).
        """

        user_prompt = f"Job Description:\n\n{job_description}"

        return self.llm.query(system_prompt, user_prompt, expect_json=True)
