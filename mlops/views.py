from django.shortcuts import render
from django.http import HttpRequest, JsonResponse
from .file_processor import file_processor

def query_rag(request: HttpRequest) -> JsonResponse:
    try:
        file_processor.process_files(request.FILES)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "error": str(e)
        })
    return JsonResponse({
        "status": "ok",
    })