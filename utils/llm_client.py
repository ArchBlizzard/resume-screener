import os
import json
from typing import Dict, Any, Optional
from openai import OpenAI
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self, api_key: Optional[str] = None):
        
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.openai_api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.provider = "openai"
        
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        
        
        if "gemini" in self.model.lower():
            self.provider = "google"
            if not self.google_api_key:
                 
                 print("Warning: GOOGLE_API_KEY not set for Gemini model.")
            else:
                genai.configure(api_key=self.google_api_key)
        else:
            if not self.openai_api_key:
                self.client = None
            else:
                self.client = OpenAI(api_key=self.openai_api_key)

    def query(self, system_prompt: str, user_prompt: str, expect_json: bool = True) -> Dict[str, Any] | str:
        if self.provider == "google":
            return self._query_google(system_prompt, user_prompt, expect_json)
        else:
            return self._query_openai(system_prompt, user_prompt, expect_json)

    def _query_google(self, system_prompt: str, user_prompt: str, expect_json: bool) -> Dict[str, Any] | str:
        try:
            model = genai.GenerativeModel(self.model)
            
            full_prompt = f"System Instruction: {system_prompt}\n\nUser Task: {user_prompt}"
            
            if expect_json:
                full_prompt += "\n\nIMPORTANT: Output ONLY valid JSON."
                
            response = model.generate_content(full_prompt)
            content = response.text
             
            if expect_json:
                return self._clean_and_parse_json(content)
            return content
        except Exception as e:
            print(f"Gemini Error: {e}")
            return {} if expect_json else ""

    def _query_openai(self, system_prompt: str, user_prompt: str, expect_json: bool) -> Dict[str, Any] | str:
        if not self.client:
            raise ValueError("OpenAI API Key not found. Please set OPENAI_API_KEY in .env or environment.")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"} if expect_json else None,
                temperature=0.2
            )
            
            content = response.choices[0].message.content
            
            if expect_json:
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                     
                    return {"error": "Failed to parse JSON response", "raw_content": content}
            
            return content

        except Exception as e:
            return {"error": f"LLM Call failed: {str(e)}"}
    
    def _clean_and_parse_json(self, content: str) -> Dict[str, Any]:
        """
        Cleans up and parses JSON from LLM output, handling common issues (extra text, code blocks, etc).
        """
        import re
        
        content = re.sub(r"^```json|^```|```$", "", content.strip(), flags=re.MULTILINE)
        
        match = re.search(r"{.*}", content, re.DOTALL)
        if match:
            json_str = match.group(0)
            try:
                return json.loads(json_str)
            except Exception as e:
                return {"error": f"Failed to parse JSON: {e}", "raw_content": content}
        else:
            return {"error": "No JSON object found in output", "raw_content": content}
