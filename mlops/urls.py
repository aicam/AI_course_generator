from django.urls import path
from . import views

urlpatterns = [
    path("query_rag", views.query_rag, name="Creating slides using RAG")
]