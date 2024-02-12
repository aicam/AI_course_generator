from django.urls import path
from . import views

urlpatterns = [
    path("query_rag", views.query_rag, name="Creating slides using RAG"),
    path("query_gpt4_vision", views.query_gpt4_vision, name="Creating slides using GPT 4 vision")
]