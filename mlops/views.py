from django.shortcuts import render
from django.http import HttpRequest, JsonResponse
from .file_processor import file_processor
from .haystack_template_processor import haystack_template_processor
from . import read_template
def query_rag(request: HttpRequest) -> JsonResponse:
    try:
        # file_processor.process_files(request.FILES)
        template = read_template("basic")
        output = haystack_template_processor.get_template_result(template)
        return JsonResponse({
            "status": "ok",
            "result": output
        })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "error": str(e)
        })