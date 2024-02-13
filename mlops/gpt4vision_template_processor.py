import os
from typing import List, Union
from openai import OpenAI
import re

from . import ComponentOutput, ComponentAttributes, WARNING_COMMAND

MODEL = "gpt-4-vision-preview"
class GPT4VisionTemplateProcessor:

    def __init__(self, openai_api_key: str):
        self.client = OpenAI(
                api_key = openai_api_key
            )

    def __call_gpt(self, content: List[dict], max_token: Union[int] = 300) -> str:
        response = self.client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": content,
                }
            ],
            max_tokens=max_token,
        )

        return response.choices[0].message.content

    def __get_component_default_result(self, component: ComponentAttributes, urls: List[str]) -> str:
        '''
        If a component does not have parameters or specific requirements, this function
        runs a default api call and answering which matches many components.
        :param component: any component
        :return: answer of the component
        '''
        content = [{
            "type": "image_url",
            "image_url": {
                "url": url
            }
        } for url in urls]
        content.append({
            "type": "text",
            "text": component.prompt
        })

        return self.__call_gpt(content)

    def __get_default_transcript(self, answer: str, urls: List[str], max_words: Union[int] = 50) -> str:
        '''
        Each component has a transcript as a text to convert to voice and play in the slide. This function
        creates a default transcript based on the answer and document.
        :param answer: answer from chatgpt
        :param max_words: maximum number of words in the speech
        :return: speech text
        '''

        content = [{
            "type": "image_url",
            "image_url": {
                "url": url
            }
        } for url in urls]
        content.append({
            "type": "text",
            "text": f'''
            You are a teacher for a course. {WARNING_COMMAND}. Write like a speaker. You have been asked to talk less than {max_words} words about the context mentioned below based on the document.
            \n\n
            Context: {answer}
        '''
        })

        return self.__call_gpt(content)

    ### functions that operate based on component_name in the template ###
    def get_title_component_result(self, component: ComponentAttributes, urls: List[str]) -> ComponentOutput:
        answer = self.__get_component_default_result(component, urls)
        transcript = self.__get_default_transcript(answer, urls)
        return ComponentOutput(answer, transcript, [])

    def get_title_fixed_component_result(self, component: ComponentAttributes, urls: List[str]) -> ComponentOutput:
        answer = component.params[0]['title']
        transcript = self.__get_default_transcript(answer, urls)
        return ComponentOutput(answer, transcript, [])

    def get_shortdescription_component_result(self, component: ComponentAttributes, urls: List[str]) -> ComponentOutput:
        answer = self.__get_component_default_result(component, urls)
        transcript = self.__get_default_transcript(answer, urls)
        return ComponentOutput(answer, transcript, [])

    def get_bulletpoint_component_result(self, component: ComponentAttributes, urls: List[str]) -> ComponentOutput:
        answer = self.__get_component_default_result(component, urls)
        transcript = self.__get_default_transcript(answer, urls)
        params = answer.split(component.delimiter)
        return ComponentOutput(answer, transcript, params)

    ### functions that operate based on component_name in the template ###

    def __run_component_no_params(self, component: ComponentAttributes, urls: List[str]) -> ComponentOutput:
        '''
        Maps component_name in template to its function in the class
        '''
        if component.component_name == 'title':
            return self.get_title_component_result(component, urls)
        elif component.component_name == 'shortdescription':
            return self.get_shortdescription_component_result(component, urls)
        elif component.component_name == 'bulletpoints':
            return self.get_bulletpoint_component_result(component, urls)
        elif component.component_name == 'title-fixed':
            return self.get_title_fixed_component_result(component, urls)

    def __parse_param_address(self, param_address: str) -> List[int]:
        pattern = r"slide_(\d+)_body_(\d+)_(\d+)"
        match = re.search(pattern, param_address)

        if match:
            return [int(x) for x in match.groups()]
        else:
            return []

    def __get_component_params_val(self, template: dict, params: List[dict]) -> List[dict]:
        params_parsed = []
        for param in params:
            param_key = list(param.keys())[0]
            param_address = param[param_key]
            param_address_int = self.__parse_param_address(param_address)
            val = template['slides'][param_address_int[0]]['body'][param_address_int[1]].output['params'][param_address_int[2]]
            params_parsed.append({
                "var": param_key,
                "val": val
            })
        return params_parsed

    def __fill_params(self, template: dict, slide_num: int) -> dict:
        header_params = template['slides'][slide_num]['header'].params
        if len(header_params) > 0:
            params_parsed = self.__get_component_params_val(template, header_params)
            prompt = template['slides'][slide_num]['header'].prompt
            rag_query = template['slides'][slide_num]['header'].rag_query
            for param in params_parsed:
                prompt = prompt.replace(f"%{param['var']}%", param['val'])
            for param in params_parsed:
                rag_query = rag_query.replace(f"%{param['var']}%", param['val'])
            template['slides'][slide_num]['header'].prompt = prompt
            template['slides'][slide_num]['header'].rag_query = rag_query
            template['slides'][slide_num]['header'].params = [{p['var']: p['val']} for p in params_parsed]

        for (i, slide) in enumerate(template['slides'][slide_num]['body']):
            if len(slide.params) > 0:
                params_parsed = self.__get_component_params_val(template, slide.params)
                prompt = template['slides'][slide_num]['body'][i].prompt
                rag_query = template['slides'][slide_num]['body'][i].rag_query
                for param in params_parsed:
                    prompt = prompt.replace(f"%{param['var']}%", param['val'])
                for param in params_parsed:
                    rag_query = rag_query.replace(f"%{param['var']}%", param['val'])
                template['slides'][slide_num]['body'][i].prompt = prompt
                template['slides'][slide_num]['body'][i].rag_query = rag_query
                template['slides'][slide_num]['body'][i].params = [{p['var']: p['val']} for p in params_parsed]

        return template

    def get_template_result(self, template: dict, urls: List[str]) -> dict:

        for (i, slide) in enumerate(template['slides']):
            print("in slide ", i)
            template = self.__fill_params(template, i)
            header_output = self.__run_component_no_params(slide['header'], urls)
            template['slides'][i]['header'].output = {
                "answer": header_output.answer,
                "transcript": header_output.transcript,
                "params": header_output.params
            }

            for (j, component) in enumerate(slide['body']):
                print("in body component ", j)
                component_output = self.__run_component_no_params(component, urls)
                template['slides'][i]['body'][j].output = {
                    "answer": component_output.answer,
                    "transcript": component_output.transcript,
                    "params": component_output.params
                }

        return template

gpt4vision_template_processor = GPT4VisionTemplateProcessor(
    openai_api_key=os.environ['OPENAI_API_KEY']
)