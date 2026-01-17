import sys
import json
import argparse
import os
import glob

from utils.llm_client import LLMClient
from agents.resume_ingestion import ResumeIngestionAgent
from agents.resume_understanding import ResumeUnderstandingAgent
from agents.job_understanding import JobUnderstandingAgent
from agents.matcher import MatchingScoringAgent
from agents.decision import DecisionAgent

def get_files(path, extensions):
    if os.path.isfile(path):
        return [path]
    elif os.path.isdir(path):
        files = []
        for ext in extensions:
            files.extend(glob.glob(os.path.join(path, f"*{ext}")))
        return files
    return []

def main():
    parser = argparse.ArgumentParser(description="Agentic Resume Screening Assistant")
    parser.add_argument("resume_path", help="Path to resume file or directory containing resumes")
    parser.add_argument("job_desc_path", help="Path to job description file or directory containing JDs")
    
    args = parser.parse_args()

    # Collect files
    resume_files = get_files(args.resume_path, ['.pdf', '.docx', '.doc'])
    job_files = get_files(args.job_desc_path, ['.txt', '.md'])

    if not resume_files:
        print(f"Error: No valid resume files found in {args.resume_path}")
        sys.exit(1)
    if not job_files:
        print(f"Error: No valid job description files found in {args.job_desc_path}")
        sys.exit(1)

    print(f"Found {len(resume_files)} resumes and {len(job_files)} job descriptions.")

    # Initialize Client
    try:
        llm = LLMClient() 
        # Check based on provider
        if llm.provider == "openai" and not getattr(llm, 'client', None):
             print("Warning: OpenAI API Key not preset. Set OPENAI_API_KEY.")
        elif llm.provider == "google" and not getattr(llm, 'google_api_key', None):
             print("Warning: Google API Key not preset. Set GOOGLE_API_KEY.")

    except Exception as e:
        print(f"Error initializing LLM Client: {e}")
        sys.exit(1)

    print("--- Starting Agentic Screening Process ---")
    
    # Initialize Agents
    ingestor = ResumeIngestionAgent()
    resume_agent = ResumeUnderstandingAgent(llm)
    job_agent = JobUnderstandingAgent(llm)
    matcher = MatchingScoringAgent(llm)
    decision_agent = DecisionAgent(llm)

    # Process all JDs
    for j_path in job_files:
        print(f"\n[JOB] Processing: {os.path.basename(j_path)}")
        try:
            with open(j_path, 'r', encoding='utf-8') as f:
                job_text = f.read()
            
            # 3. Job Understanding (Once per Job)
            job_data = job_agent.analyze(job_text)
        except Exception as e:
            print(f"Failed to process job {j_path}: {e}")
            continue

        # Process all Resumes for this JD
        for r_path in resume_files:
            print(f"  > [RESUME] Screening: {os.path.basename(r_path)}")
            try:
                # 1. Ingestion
                ingest_result = ingestor.ingest(r_path)
                if not ingest_result["success"]:
                    print(f"    x Error Ingesting Resume: {ingest_result['error']}")
                    continue
                
                resume_text = ingest_result["text"]

                # 2. Resume Understanding
                resume_data = resume_agent.analyze(resume_text)

                # 4. Matching
                match_analysis = matcher.match(resume_data, job_data)

                # 5. Decision
                final_decision = decision_agent.decide(match_analysis)
                
                # Output brief result
                print(f"    = Result: {final_decision.get('recommendation')} (Score: {final_decision.get('match_score')})")
                print(f"      Reason: {final_decision.get('reasoning_summary')}")

            except Exception as e:
                print(f"    x Error screening resume {r_path}: {e}")

if __name__ == "__main__":
    main()
