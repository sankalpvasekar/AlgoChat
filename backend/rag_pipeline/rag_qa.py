import os
import sys
import json

# Add rag_pipeline to sys.path so its internal modules can refer to each other
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from retrieval.retrieve import retrieve_top_chunks
from groq import Groq

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '.env'))

# ---------------- SETTINGS ----------------
API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    print("WARNING: GROQ_API_KEY not found in environment. Socratic Tutor will fail.")
    client = None
else:
    client = Groq(api_key=API_KEY)

# ---------------- MEMORY STORE ----------------
# Simple in-memory prototype for Short-term memory conversation history
SESSIONS = {}

# ---------------- SOCRATIC PROMPT TEMPLATE ----------------
SOCRATIC_SYSTEM_PROMPT = """You are an experienced and patient computer science teacher who specializes in teaching Data Structures and Algorithms (DSA).
Goal: Teach like a human teacher in a classroom using an interactive Socratic method. DO NOT give long lecture-style explanations.

Strict Teaching Principles:
1. Short Chunks: Explain in medium-sized chunks (5–8 lines). Never give long paragraphs.
2. Mandatory Questions: After each chunk, pause and ask a curiosity, prediction, or reasoning question.
3. Teaching Loop:
   - Start with a real-life curiosity question.
   - Introduce concepts gradually (chunked).
   - Use diagrams for visualization (Stack, List, Tree, etc.).
   - Ask for reasoning/predictions.
4. Formatting:
   - Explanation -> Diagram/Example -> Question -> STOP.
5. Adaptive: Scale difficulty based on student answers. Simplify if they are confused.
6. Visualization:
   - Use ASCII diagrams for stacks/lists/trees.
   - Also include a specialized `d3-json` block for frontend visualization:
     ```d3-json
     {
       "concept": "Name",
       "type": "linear" | "tree",
       "steps": [
         { "elements": ["val1", "val2"], "description": "Step 1" }
       ]
     }
     ```

Example Style:
Teacher: Imagine a pile of plates. Which do you take first? (Top/Bottom?)
(Wait)
Teacher: Correct! That's LIFO. Stacks work like this. [Diagram]
How would we remove 'X' from this stack?
"""

# ---------------- FUNCTION TO ASK QUESTIONS ----------------
def ask_question_stream(query, session_id="default", top_k=5, custom_history_text=None):
    """
    Generator version of ask_question that yields response chunks.
    """
    # 1 Retrieve chunks from FAISS
    top_chunks = retrieve_top_chunks(query, top_k)
    context = "\n\n".join(top_chunks)

    # 2 Load history
    if custom_history_text is not None:
        history_text = custom_history_text
    else:
        convo_history = SESSIONS.get(session_id, [])[-6:]
        history_text = "\n".join([f"{msg['role'].capitalize()}: {msg['text']}" for msg in convo_history])

    # 3 Stream from LLM
    try:
        stream = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SOCRATIC_SYSTEM_PROMPT},
                {"role": "user", "content": f"Reference Knowledge:\n{context}\n\nPrevious History:\n{history_text}\n\nStudent Query: {query}"}
            ],
            model="llama-3.3-70b-versatile",
            stream=True,
        )
        
        full_response = ""
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                full_response += content
                yield content
                
        # Update Memory after full stream completion
        if custom_history_text is None:
            if session_id not in SESSIONS: SESSIONS[session_id] = []
            SESSIONS[session_id].append({"role": "user", "text": query})
            SESSIONS[session_id].append({"role": "assistant", "text": full_response})
            
    except Exception as e:
        yield f" Error: {str(e)}"

def ask_question(query, session_id="default", top_k=5, custom_history_text=None):

    # 1 Retrieve chunks from FAISS
    top_chunks = retrieve_top_chunks(query, top_k)
    context = "\n\n".join(top_chunks)

    # 2 Load or Init Memory Profile
    if custom_history_text is not None:
        history_text = custom_history_text
    else:
        if session_id not in SESSIONS:
            SESSIONS[session_id] = []
        
        # Keep only the last 6 turns to prevent overwhelming context length
        convo_history = SESSIONS[session_id][-6:]
        history_text = "\n".join([f"{msg['role'].capitalize()}: {msg['text']}" for msg in convo_history])

    # 3 Create prompt
    prompt = f"""
{SOCRATIC_SYSTEM_PROMPT}

Use the following reference knowledge:
{context}

Use the previous conversation as context:
{history_text}

The student asked: "{query}"
"""

    # 4 AI Tutor Response (Socratic)
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SOCRATIC_SYSTEM_PROMPT},
                {"role": "user", "content": f"Reference Knowledge:\n{context}\n\nPrevious History:\n{history_text}\n\nStudent Query: {query}"}
            ],
            model="llama-3.3-70b-versatile",
        )
        answer = chat_completion.choices[0].message.content
        
        # 5 Update Memory
        if custom_history_text is None:
            SESSIONS[session_id].append({"role": "user", "text": query})
            SESSIONS[session_id].append({"role": "assistant", "text": answer})
        return answer
    except Exception as e:
        print(f"Socratic Tutor Error: {e}")
        return f"I'm sorry, I'm having a bit of trouble connecting to my reasoning engine right now. (Error: {str(e)})"


import subprocess
import tempfile

def run_python_code(code, input_data="", timeout=5):
    """
    Executes Python code in a subprocess and returns the output/errors.
    Supports standard input (stdin).
    """
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w', encoding='utf-8') as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            [sys.executable, tmp_path],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        output = result.stdout
        error = result.stderr
        
        # Combine stdout and stderr for a more complete execution picture
        combined_output = ""
        if output:
            combined_output += output
        if error:
            if combined_output:
                combined_output += "\n"
            combined_output += error
            
        return combined_output if combined_output else "No output."
    except subprocess.TimeoutExpired:
        return "Error: Execution timed out (max 5 seconds)."
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

from agents.codellama_agent import analyze_logic_with_codellama

def analyze_code(code, execute_output, goal, session_id="practice_default"):
    """
    Code Analysis Function
    instructs Groq to provide Socratic hints on user code without giving away the direct solution.
    Incorporates deep logical analysis from Code Llama.
    """
    # 1. Perform deep logical analysis using Code Llama
    logic_analysis = analyze_logic_with_codellama(code, execute_output)
    
    analysis_context = ""
    if logic_analysis.get("has_error"):
        analysis_context = f"""
Deep Logical Analysis Results:
- Category: {logic_analysis.get('category')}
- Technical Issue: {logic_analysis.get('issue_summary')}
- Suggested Tutor Direction: {logic_analysis.get('suggestion_for_tutor')}
"""

    prompt = f"""You are an experienced and patient CS Teacher helping a student with their code.
Your goal is to guide them SOCRATICALLY to find their own mistake. DO NOT give corrected code.

Student Goal: "{goal}"
Student Code:
```python
{code}
```
Program Output:
```
{execute_output}
```
{analysis_context}

Follow the CS Teacher Principles:
1. Explanation: 5-8 lines max. Simple terms.
2. Visual: Generate a Mermaid diagram or ASCII diagram showing the program flow or data state.
3. Question: Ask a reasoning question to help them find the bug (e.g., "What value is 'x' at line 5?").

Rules:
- NO full solutions.
- One chunk at a time.
- If it's an EOFError, point them to the STDIN box.

Format:
Explanation: <text>
Diagram: <mermaid or ascii>
Question: <text>
"""
    # 2. AI Tutor Response (Socratic analysis)
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Analysis Error: {e}")
        return f"Explanation: I'm having trouble analyzing your code right now.\n\nGuiding Question: Can you try running it again?\n\nHint: Check your connection.\n\n(Error: {str(e)})"



def process_video_transcript(transcript, session_id="video_default"):
    """
    Uses Groq to break a video transcript into logical 'Learning Steps'.
    Each step includes a summary and a Socratic guiding question.
    """
    prompt = f"""You are a Socratic learning assistant. A student is watching a video with this transcript:
{transcript[:6000]} # Increased context for better step identification

Task:
1. Identify 3-5 key logical concepts or steps explained in this video segment.
2. For each concept, provide:
   - "step": The sequence number (1, 2, 3...).
   - "title": A short title for this step.
   - "explanation": A very simple, 2-sentence explanation of the concept.
   - "question": A question to check the student's understanding of this specific step.

Return the response as a strict JSON object with a single key "steps" containing an array of these objects:
{{
  "steps": [
    {{
      "step": 1,
      "title": "Concept Name",
      "explanation": "Simple explanation...",
      "question": "Socratic question..."
    }}
  ]
}}
"""
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        data = json.loads(chat_completion.choices[0].message.content)
        # Handle cases where LLM returns a root object instead of array
        if isinstance(data, dict) and "steps" in data:
            return data["steps"]
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"Transcript processing failed: {str(e)}")
        return []

# ---------------- INTERACTIVE MODE ----------------
if __name__ == "__main__":

    print("=== RAG QA SYSTEM USING GEMINI ===")

    while True:

        query = input("\nEnter your question (or 'exit' to quit): ")

        if query.lower() == "exit":
            break

        answer = ask_question(query)

        print("\nAnswer:\n", answer)
