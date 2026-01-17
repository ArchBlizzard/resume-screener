# Agentic Resume Screening & Shortlisting Assistant

A local Python backend project that uses a multi-agent architecture to screen resumes against job descriptions.

## Architecture

The system is designed as a pipeline of specialized agents, each communicating via structured data (JSON):

1.  **ResumeIngestionAgent**: 
    *   **Responsibility**: Text extraction from PDF/DOCX.
    *   **Input**: File path.
    *   **Output**: Raw text.
2.  **ResumeUnderstandingAgent**: 
    *   **Responsibility**: Semantic parsing of resume text.
    *   **Input**: Raw resume text.
    *   **Output**: Structured Profile (Skills, Experience, Roles, Education).
3.  **JobUnderstandingAgent**: 
    *   **Responsibility**: Extracts requirements from Job Description (JD).
    *   **Input**: JD text.
    *   **Output**: Structured Requirements (Required Skills, Role Level, etc.).
4.  **MatchingScoringAgent**: 
    *   **Responsibility**: Logical comparison of Profile vs Requirements.
    *   **Input**: Profile JSON + Requirements JSON.
    *   **Output**: Match Analysis (Score, Gaps, Strengths).
5.  **DecisionAgent**: 
    *   **Responsibility**: Final hiring recommendation.
    *   **Input**: Match Analysis.
    *   **Output**: Final Decision (Proceed/Reject/Review, Reason).

### Flow
`File -> [Ingestion] -> Text -> [ResumeUnderstanding] -> Profile`
`JD File -> Text -> [JobUnderstanding] -> Requirements`
`(Profile + Requirements) -> [Matcher] -> Analysis -> [Decision] -> JSON Result`

---

## Setup & Run Instructions

### Prerequisites
*   Python 3.10+
*   OpenAI API Key (or compatible LLM endpoint)

### Installation

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Set up environment variables:
    *   Create a `.env` file in the root.
    *   Add your key: `OPENAI_API_KEY=sk-....`
    *   (Optional) `LLM_MODEL=gpt-4o`

### Usage

Run the `main.py` script with paths to your resume and job description:

```bash
python main.py path/to/resume.pdf path/to/job_description.txt
```

---

## Sample Inputs & Outputs

### Input
**Resume**: (A PDF containing Python, Machine Learning, 3 years exp)
**Job Description**: 
> "looking for a Senior Python Developer with 5+ years experience and AWS knowledge."

### Output (Console JSON)
```json
{
  "match_score": 0.65,
  "recommendation": "Needs manual review",
  "requires_human": true,
  "confidence": 0.85,
  "reasoning_summary": "The candidate has strong Python skills but falls short of the 5+ years experience requirement (estimated 3 years). They also lack clear AWS experience mentioned in the resume. However, the core Python capability suggests they might be a fit for a mid-level role."
}
```

---

## Assumptions & Trade-offs
*   **LLM Dependency**: Requires an internet connection and API credits.
*   **Parsing**: PDF parsing is complex; complex layouts might yield messy text, but the LLM is generally robust at cleaning it up.
*   **Local**: No database is used; specific run-to-run state is not preserved.
*   **Privacy**: Resume text is sent to the LLM provider. Ensure compliance before using with real private data.
