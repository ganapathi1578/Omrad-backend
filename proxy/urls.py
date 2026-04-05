# proxy/urls.py
from django.urls import path
from .views import gemini_proxy_view

urlpatterns = [
    path('chat/', gemini_proxy_view, name='gemini-chat'),
]