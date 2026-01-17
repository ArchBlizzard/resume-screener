import json
from typing import Dict, Any
from utils.llm_client import LLMClient

class MatchingScoringAgent:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def match(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compares specific resume data against job requirements.
        """
        
        system_prompt = """
        You are a hiring manager's assistant. Evaluate the fit between the Candidate Profile and Job Requirements.
        
        Output JSON:
        {
            "match_score": float (0.0 to 1.0),
            "matching_skills": ["list"],
            "missing_critical_skills": ["list"],
            "experience_match": "Low | Medium | High | Overqualified",
            "strengths": ["list of strong points"],
            "gaps": ["list of concerning gaps or mismatches"],
            "uncertainty_flag": boolean (true if resume info is insufficient to decide)
        }
        
        Be critical. A perfect 1.0 score should be rare. 
        Focus on whether 'required_skills' from the job are present in the 'skills' or 'roles' of the candidate.
        """

        # We serialize the inputs to string for the prompt
        user_prompt = f"""
        Candidate Profile:
        {json.dumps(resume_data, indent=2)}

        Job Requirements:
        {json.dumps(job_data, indent=2)}
        """

        return self.llm.query(system_prompt, user_prompt, expect_json=True)
