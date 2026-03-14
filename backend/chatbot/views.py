import json
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as django_login
from django.contrib.auth.models import User
from rag_pipeline.rag_qa import ask_question, ask_question_stream, analyze_code, process_video_transcript
from rag_pipeline.transcript_service import extract_video_id, get_transcript
from rag_pipeline.video_processor import chunk_transcript
from rag_pipeline.video_rag import index_video_transcript, query_video_rag
from .models import Conversation, Message

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '')
            name = data.get('name', '')
            
            # Simple mock authentication for now, matching React's mock
            # In production, use authenticate(username=email, password=password)
            if name and email:
                user, created = User.objects.get_or_create(
                    username=email,
                    defaults={'first_name': name, 'email': email}
                )
                
                # We mock the session/login
                django_login(request, user)
                
                return JsonResponse({
                    'id': user.id,
                    'name': user.first_name,
                    'email': user.email,
                    'role': 'student',
                    'success': True
                })
            else:
                return JsonResponse({'error': 'Name and Email required'}, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
            
    return JsonResponse({'error': 'Method not allowed. Use POST.'}, status=405)

@csrf_exempt
def get_conversations(request):
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'user_id required'}, status=400)
        
        try:
            conversations = Conversation.objects.filter(user_id=user_id).order_by('-updated_at')
            data = [{
                'id': conv.session_id,
                'title': conv.title,
                'updated_at': conv.updated_at.isoformat()
            } for conv in conversations]
            return JsonResponse({'conversations': data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed. Use GET.'}, status=405)

@csrf_exempt
def get_messages(request, session_id):
    if request.method == 'GET':
        try:
            conversation = Conversation.objects.get(session_id=session_id)
            messages = conversation.messages.all().order_by('timestamp')
            data = [{
                'role': msg.role,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat()
            } for msg in messages]
            return JsonResponse({'messages': data})
        except Conversation.DoesNotExist:
            return JsonResponse({'messages': []})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed. Use GET.'}, status=405)

@csrf_exempt
def ask_rag(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query', '')
            session_id = data.get('session_id', 'default_session')
            user_id = data.get('user_id')
            
            if not query:
                return JsonResponse({'error': 'No query provided'}, status=400)
            
            # Call our RAG pipeline, passing session_id for continuity
            user = User.objects.filter(id=user_id).first() if user_id else None
            
            conversation, created = Conversation.objects.get_or_create(
                session_id=session_id,
                defaults={
                    'user': user,
                    'title': query[:25] + "..." if len(query) > 25 else query
                }
            )
            
            # Build history text
            messages = conversation.messages.all().order_by('timestamp')
            recent_messages = messages[max(0, len(messages) - 6):]
            if recent_messages:
                history_text = "\n".join([f"{msg.role.capitalize()}: {msg.content}" for msg in recent_messages])
            else:
                history_text = ""
            
            # Using streaming response
            def stream_generator():
                full_text = ""
                for chunk in ask_question_stream(query, session_id=session_id, custom_history_text=history_text):
                    full_text += chunk
                    yield chunk
                
                # After stream ends, save final assistant message to DB
                Message.objects.create(conversation=conversation, role='user', content=query)
                Message.objects.create(conversation=conversation, role='assistant', content=full_text)
                conversation.save()

            return StreamingHttpResponse(stream_generator(), content_type='text/plain')
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Method not allowed. Use POST.'}, status=405)


from rag_pipeline.rag_qa import ask_question, analyze_code, run_python_code

@csrf_exempt
def analyze_practice_code(request):
    """
    Receives code and execution output parameters to generate Socratic hints.
    Now supports backend Python execution.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code', '')
            stdin = data.get('stdin', '')
            goal = data.get('goal', 'Improve general coding skills')
            session_id = data.get('session_id', 'practice_default')
            
            if not code:
                return JsonResponse({'error': 'No code provided'}, status=400)

            # Execute Python code on the backend with stdin support
            execution_output = run_python_code(code, input_data=stdin)
                
            hints = analyze_code(code, execution_output, goal, session_id)
            return JsonResponse({
                'hints': hints,
                'execution_output': execution_output
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Method not allowed. Use POST.'}, status=405)
@csrf_exempt
def process_video(request):
    """
    Extracts transcript from a YouTube URL and generates Socratic learning steps.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            url = data.get('url', '')
            
            if not url:
                return JsonResponse({'error': 'No URL provided'}, status=400)
            
            video_id = extract_video_id(url)
            if not video_id:
                return JsonResponse({'error': 'Invalid YouTube URL'}, status=400)
            
            transcript = get_transcript(video_id)
            if not transcript:
                return JsonResponse({'error': 'Could not extract transcript. Video might not have captions.'}, status=404)
            
            # Phase 5: Create Video RAG Index
            # Fetch snippet version for indexing
            snippets = get_transcript(video_id, return_snippets=True)
            if snippets:
                chunks = chunk_transcript(snippets)
                index_video_transcript(video_id, chunks)

            steps = process_video_transcript(transcript)
            
            if not steps:
                return JsonResponse({
                    'error': 'Video is too short or logic could not be extracted. Try a coding tutorial!'
                }, status=422)

            return JsonResponse({
                'video_id': video_id,
                'steps': steps
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Method not allowed. Use POST.'}, status=405)
@csrf_exempt
def video_chat(request):
    """
    RAG-based chat for a specific video.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            video_id = data.get('video_id', '')
            query = data.get('query', '')
            
            if not video_id or not query:
                return JsonResponse({'error': 'video_id and query are required'}, status=400)
            
            # 1. Retrieve context
            context_chunks = query_video_rag(video_id, query)
            if not context_chunks:
                # Fallback to general knowledge if video index isn't found
                context_text = "No specific transcript context found for this video."
            else:
                # Format context with timestamps
                context_parts = []
                for c in context_chunks:
                    ts = int(c['timestamp'])
                    minutes = ts // 60
                    seconds = ts % 60
                    time_str = f"{minutes}:{seconds:02d}"
                    context_parts.append(f"[{time_str}] {c['text']}")
                context_text = "\n\n".join(context_parts)
            
            # 2. Call LLM (Streaming)
            import os
            from groq import Groq
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            
            prompt = f"""
            You are an experienced and patient computer science teacher specializing in DSA.
            Goal: Answer the user's question about the video transcript using the interactive Socratic method.
            
            Context from video transcript:
            {context_text}

            Strict Teaching Principles:
            1. Teach in medium-sized chunks (5–8 lines). Use context from the transcript.
            2. Never give long paragraphs.
            3. Use real-life analogies for curiosity.
            4. Show a diagram (ASCII or Mermaid) to help visualize the concept from the video.
            5. ALWAYS mention relevant timestamps (e.g., [2:15]) if applicable from context.
            6. After the explanation and diagram, ask a reasoning question and STOP.

            Format:
            Explanation: <short 5-8 line text>
            Visual: <ASCII/Mermaid diagram>
            Question: <the reasoning question>

            User Question:
            {query}
            """
            
            def stream_video_response():
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5,
                    stream=True
                )
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content

            return StreamingHttpResponse(stream_video_response(), content_type='text/plain')
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Method not allowed. Use POST.'}, status=405)
