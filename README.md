# Agentic Resume Screening & Shortlisting Assistant

A local Python backend project that uses a multi-agent architecture to screen resumes against job descriptions using LLMs (OpenAI or Gemini).

## Architecture Overview

The system is a pipeline of specialized agents, each with a single responsibility and communicating via structured JSON:

1. **ResumeIngestionAgent**
   - Extracts raw text from PDF/DOCX resumes.
   - Handles file errors and unreadable content gracefully.
2. **ResumeUnderstandingAgent**
   - Uses an LLM to parse resume text into structured data: skills, experience, roles, education, missing info.
3. **JobUnderstandingAgent**
   - Uses an LLM to extract structured requirements from a job description: required/preferred skills, experience, education, role level.
4. **MatchingScoringAgent**
   - Uses an LLM to compare candidate profile and job requirements, outputting match score, strengths, gaps, and uncertainty flag.
5. **DecisionAgent**
   - Uses an LLM to make a final structured recommendation (proceed/reject/review), with confidence and clear reasoning.

### Agent Flow

```
Resume File -> [ResumeIngestionAgent] -> Resume Text
           -> [ResumeUnderstandingAgent] -> Candidate Profile
Job Desc   -> [JobUnderstandingAgent] -> Job Requirements
(Candidate Profile + Job Requirements) -> [MatchingScoringAgent] -> Match Analysis
Match Analysis -> [DecisionAgent] -> Final JSON Decision
```

---

## Prompt Strategy
- Each agent using an LLM has a dedicated, focused prompt for its task.
- Prompts instruct the LLM to output only valid JSON, and the code robustly parses/cleans the output.
- The pipeline is modular: each agent's output is the next agent's input.

---

## Trade-offs & Assumptions
- **LLM Dependency:** Requires internet and API credits (OpenAI or Google Gemini).
- **Privacy:** Resume/job text is sent to the LLM provider. Do not use with sensitive data unless compliant.
- **Parsing:** PDF/DOCX parsing is best-effort; complex layouts may reduce accuracy, but LLMs are robust to noise.
- **No Database:** Stateless, local-only, no persistent storage.
- **Uncertainty Handling:** If info is missing or ambiguous, the system flags for human review.

---

## Error Handling
- All file and parsing errors are caught and reported.
- LLM failures (bad/missing output, quota exceeded) are handled gracefully.
- If a resume or JD cannot be processed, the error is shown and the pipeline continues.

---

## Setup & Run Instructions

### Prerequisites
- Python 3.10+
- API key for either OpenAI or Google Gemini

### Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your `.env` file in the project root:
   - For OpenAI:
     ```
     OPENAI_API_KEY=sk-...
     LLM_MODEL=gpt-4o
     ```
   - For Gemini:
     ```
     GOOGLE_API_KEY=your_gemini_key
     LLM_MODEL=gemini-2.5-flash
     ```

### Usage

You can process a single resume and JD, or entire folders:

```bash
python main.py path/to/resume.pdf path/to/job_description.txt
# or
python main.py resumes/ job-descriptions/
```

- The script will process all combinations of resumes and JDs if folders are given.
- Output is printed to the console for each pair.

---

## Sample Inputs & Outputs

### Input Example
- **Resume:** `resume_04_vikram_singh.pdf` (Freelance Full Stack Developer)
- **Job Description:** `jd_04_vague_ambiguous.txt`
  > "Looking for software developer to join our team. Should be good at coding... Programming knowledge, Database experience, Should be a team player"

### Output Example
```json
{
  "match_score": 0.6,
  "recommendation": "Needs manual review",
  "requires_human": true,
  "confidence": 0.7,
  "reasoning_summary": "The candidate has a moderate match score of 0.6 and strong technical skills in backend development, databases, and cloud platforms, exceeding the minimum experience requirement. However, critical soft skills such as 'Team player' and 'Good communication' are not explicitly demonstrated, and while they show a capacity to learn, further assessment of their learning agility and fit for a traditional mid-level role is needed due to their freelance experience. The presence of the uncertainty flag further necessitates a manual review to evaluate these qualitative aspects."
}
```


