from django.contrib import admin
from django.urls import path
from chatbot.views import ask_rag, analyze_practice_code, login_view, get_conversations, get_messages, process_video, video_chat

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # All API endpoints now under /api/
    path('api/login/', login_view, name='login'),
    path('api/conversations/', get_conversations, name='conversations'),
    path('api/messages/<str:session_id>/', get_messages, name='messages'),
    
    path('api/ask/', ask_rag, name='ask'),
    path('api/analyze/', analyze_practice_code, name='analyze'),
    
    path('api/video/process/', process_video, name='process_video'),
    path('api/video/chat/', video_chat, name='video_chat'),
]
