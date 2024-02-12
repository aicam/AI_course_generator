from django.http import JsonResponse as JsonResponseSuper
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpRequest

from .file_processor import file_processor
from .haystack_template_processor import haystack_template_processor
from .gpt4vision_template_processor import gpt4vision_template_processor
from . import read_template

class JsonEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if callable(getattr(obj, "toJSON", None)):
            return obj.toJSON()

        return super(obj)
def JsonResponse(obj):
    return JsonResponseSuper(obj,encoder=JsonEncoder)

def query_rag(request: HttpRequest) -> JsonResponse:
    '''
    Path to run RAG over document and generate course
    :param request: file in PDF format
    :return: template + output of each component
    '''
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

def query_gpt4_vision(request: HttpRequest) -> JsonResponse:
    try:
        urls, err = file_processor.process_images(request.FILES)
        if err is not None:
            return JsonResponse({
                "status": "error",
                "result": err
            })
        print(urls[0][:50])
        template = read_template("basic")
        result = gpt4vision_template_processor.get_template_result(template, urls)
        return JsonResponse({
            "status": "ok",
            "result": result
        })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "error": str(e)
        })