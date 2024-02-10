import os
import json
from dataclasses import dataclass
from typing import List

TEMP_PATH = 'mlops/tmp/'
TEMP_PROCESSED_PATH = 'mlops/tmp_processed/'
DELIMITER = '+++'

@dataclass
class ComponentAttributes:
    component_name: str
    prompt: List[str]
    params: List[dict]
    rag_query: str
    delimiter: str
    output: dict

@dataclass
class ComponentOutput:
    answer: str
    transcript: str
    params: List[str]

def read_template(name: str) -> dict:
    '''
    This function only parse slides attribute in the template to replace
    dictionaries with ComponentAttribute class
    :param name: name of the template
    :return: template json format but slides replaced with the ComponentAttribute class
    '''
    with open(f"mlops/templates/{name}.json") as f:
        template_json = json.load(f)

    for (i, slide) in enumerate(template_json['slides']):
        component = ComponentAttributes(slide['header']['component_name'],
                                        slide['header']['prompt'],
                                        slide['header']['params'],
                                        slide['header']['rag_query'],
                                        slide['header']['delimiter'],
                                        {})
        template_json['slides'][i]['header'] = component

        for (j, component_js) in enumerate(slide['body']):
            component = ComponentAttributes(component_js['component_name'],
                                            component_js['prompt'],
                                            component_js['params'],
                                            component_js['rag_query'],
                                            component_js['delimiter'],
                                            {})
            template_json['slides'][i]['body'][j] = component

    return template_json

if not os.path.exists(TEMP_PATH):
    os.mkdir(TEMP_PATH)
if not os.path.exists(TEMP_PROCESSED_PATH):
    os.mkdir(TEMP_PROCESSED_PATH)