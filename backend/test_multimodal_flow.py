import sys
import os
import json

# Add backend to sys.path
backend_path = r'c:\Users\DDR\Documents\Django\GEN_AI_ASSISTANT\backend'
if backend_path not in sys.path:
    sys.path.append(backend_path)

from rag_pipeline.rag_qa import analyze_code

# A piece of code with a logical flaw (infinite loop or logic error)
code = """
def find_sum(n):
    total = 0
    i = 1
    while i <= n:
        total += i
        # Missing i += 1, causes infinite loop
    return total

print(find_sum(5))
"""

execute_output = "Error: Execution timed out (max 5 seconds)."
goal = "Learn how to use while loops and avoid infinite loops."

print("--- Testing Code Analysis Flow ---")
hints = analyze_code(code, execute_output, goal)
print(f"AI Tutor Response:\n{hints}")

if "Mermaid Diagram:" in hints:
    print("\nSUCCESS: Mermaid diagram generated.")
if "Explanation:" in hints:
    print("SUCCESS: Socratic explanation generated.")
if "while" in hints.lower():
    print("SUCCESS: Contextually relevant hints found.")
