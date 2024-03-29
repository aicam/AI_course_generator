import os
import json
from dataclasses import dataclass
from typing import List

TEMP_PATH = 'mlops/tmp/'
TEMP_PROCESSED_PATH = 'mlops/tmp_processed/'
DELIMITER = '+++'
WARNING_COMMAND = "Only write the answer and write in a concise and direct form while retaining the essential meaning."

@dataclass
class ComponentAttributes:
    component_name: str
    prompt: str
    params: List[dict]
    rag_query: str
    delimiter: str
    output: dict

    def toJSON(self):
        """Returns a dictionary representation of the object attributes.

        This method converts the attributes of the `ComponentAttributes`
        instance to a dictionary, ensuring JSON serializability.

        Returns:
            dict: A dictionary containing the instance's attributes.
        """

        return {
            'component_name': self.component_name,
            'prompt': self.prompt,
            'params': self.params,
            'rag_query': self.rag_query,
            'delimiter': self.delimiter,
            'output': self.output,
        }
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