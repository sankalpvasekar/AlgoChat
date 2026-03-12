import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()


from rag_pipeline.rag_qa import ask_question, analyze_code

print("Testing RAG pipeline direct call...")
try:
    print("Asking question...")
    answer = ask_question("explain binary search", session_id="test1")
    print("Answer:")
    print(answer)
except Exception as e:
    print(f"Exception during ask_question: {repr(e)}")
