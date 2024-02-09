import json
from dataclasses import dataclass
from typing import List

from .haystack_adopter import haystack_adopter

@dataclass
class ComponentAttributes:
    component_name: str
    prompt: List[str]
    params: List[str]
    rag_query: str
    delimiter: str


class TemplateProcessor:

    def __int__(self):
        self.templates_path = "templates"

    def read_template(self, name: str) -> dict:

        with open(f"{self.templates_path}/{name}") as f:
            template_json = json.load(f)

        for (i, slide) in enumerate(template_json['slides']):
            component = ComponentAttributes(slide['header']['component_name'],
                                            slide['header']['prompts'],
                                            slide['header']['params'],
                                            slide['header']['rag_query'],
                                            slide['header']['delimiter'])
            template_json['slides'][i]['header'] = component

            for (j, component_js) in enumerate(slide['body']):
                component = ComponentAttributes(component_js['component_name'],
                                                component_js['prompts'],
                                                component_js['params'],
                                                component_js['rag_query'],
                                                component_js['delimiter'])
                template_json['slides'][i]['body'][j] = component

        return template_json

    def get_haystack_title_component_result(self, component: ComponentAttributes, context: str):
        prompt = '''
            Synthesize a title from the context provided below. It will be a title for the first slide
            of a course powerpoint. %s.
        ''' % component.prompt
        prompt_node = haystack_adopter.get_prompt_node()

        return haystack_adopter.get_prompt_node()