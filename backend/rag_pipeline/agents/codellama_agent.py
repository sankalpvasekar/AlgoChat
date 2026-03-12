import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_logic_with_codellama(code, execute_output):
    """
    Uses a code-specialized model (Llama 3 70B via Groq) to perform deep logical analysis.
    Identifies logical bugs, edge case failures, and efficiency issues.
    """
    prompt = f"""You are an expert software engineer performing a deep logical analysis of a student's code.
Your goal is to identify precise logical mistakes, missing steps, or efficiency issues.

Student Code:
```python
{code}
```

Execution Output:
```
{execute_output}
```

Tasks:
1. Identify the primary logical error (if any) that isn't just a syntax error.
2. Check for missing edge cases (e.g., negative numbers, empty input).
3. Check for infinite loops or resource exhaustions.
4. Categorize the issue (logical, efficiency, edge_case, or none).

Return your findings in a strict JSON format:
{{
  "has_error": true/false,
  "category": "logical" | "efficiency" | "edge_case" | "none",
  "issue_summary": "Short technical description of the logical flaw",
  "technical_details": "Precise explanation of why the logic fails",
  "suggestion_for_tutor": "A hint on how a Socratic tutor should guide the student to this realization"
}}
"""
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile", # Using Llama 3.3 70B as it's state-of-the-art for reasoning
            response_format={"type": "json_object"}
        )
        return json.loads(chat_completion.choices[0].message.content)
    except Exception as e:
        return {
            "has_error": False,
            "category": "none",
            "issue_summary": f"Analysis failed: {str(e)}",
            "technical_details": "",
            "suggestion_for_tutor": ""
        }
