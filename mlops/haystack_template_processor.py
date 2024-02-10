from typing import List, Union
import re

from .haystack_adopter import haystack_adopter
from . import ComponentOutput, ComponentAttributes

TOP_K = 2
WARNING_COMMAND = "Only write the answer."


class HaystackTemplateProcessor:

    def __get_component_default_result(self, component: ComponentAttributes, only_context: Union[bool] = False) -> (str, str):
        '''
        If a component does not have parameters or specific requirements, this function
        runs a default retrieving and answering which matches many components.
        :param component: any component
        :return: answer of the component and the context which RAG has found
        '''
        document_store = haystack_adopter.get_document_store("test")
        retriever = haystack_adopter.get_retriever(document_store)
        context_doc = retriever.retrieve(component.rag_query, top_k=TOP_K)
        context = '\n'.join([x.content for x in context_doc])
        if only_context:
            return "", context
        prompt = f'''
                    Synthesize an answer from the context provided below. {WARNING_COMMAND}.
                    {component.prompt}. 
                    Context: {context}
                '''
        prompt_node = haystack_adopter.get_prompt_node()
        answer = prompt_node(prompt)[0]
        return answer, context

    def __get_default_transcript(self, answer: str, context: str, max_words: Union[int] = 50) -> str:
        prompt_node = haystack_adopter.get_prompt_node()
        prompt = f'''
            You are a teacher for a course. {WARNING_COMMAND}. Write like a speaker, do not point at the paragraph. You have been asked to talk less than {max_words} words about a paragraph with respect to the context.
            In the following, you see a paragraph and a context, you should talk about the paragraph and get help from the context.
            \n\n
            Context: {context}
            \n\n
            Paragraph: {answer}
        '''
        return prompt_node(prompt)[0]

    def get_title_component_result(self, component: ComponentAttributes) -> ComponentOutput:
        answer, context = self.__get_component_default_result(component)
        transcript = self.__get_default_transcript(answer, context)
        return ComponentOutput(answer, transcript, [])

    def get_title_fixed_component_result(self, component: ComponentAttributes) -> ComponentOutput:
        print("in fixed ", component)
        answer = component.params[0]['title']
        _, context = self.__get_component_default_result(component, True)
        transcript = self.__get_default_transcript(answer, context)
        print("in fixed finished")
        return ComponentOutput(answer, transcript, [])

    def get_shortdescription_component_result(self, component: ComponentAttributes) -> ComponentOutput:
        answer, context = self.__get_component_default_result(component)
        transcript = self.__get_default_transcript(answer, context)
        return ComponentOutput(answer, transcript, [])

    def get_bulletpoint_component_result(self, component: ComponentAttributes) -> ComponentOutput:
        answer, context = self.__get_component_default_result(component)
        transcript = self.__get_default_transcript(answer, context)
        params = answer.split(component.delimiter)
        return ComponentOutput(answer, transcript, params)

    def __run_component_no_params(self, component: ComponentAttributes) -> ComponentOutput:
        if component.component_name == 'title':
            return self.get_title_component_result(component)
        elif component.component_name == 'shortdescription':
            return self.get_shortdescription_component_result(component)
        elif component.component_name == 'bulletpoints':
            return self.get_bulletpoint_component_result(component)
        elif component.component_name == 'title-fixed':
            return self.get_title_fixed_component_result(component)

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
        print(f"filling params slide {slide_num} start")
        if len(header_params) > 0:
            params_parsed = self.__get_component_params_val(template, header_params)
            print("header params parsed ", params_parsed)
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
                print(f"slide {slide_num} body {i}")
                params_parsed = self.__get_component_params_val(template, slide.params)
                print("params parsed ", params_parsed)
                prompt = template['slides'][slide_num]['body'][i].prompt
                rag_query = template['slides'][slide_num]['body'][i].rag_query
                for param in params_parsed:
                    prompt = prompt.replace(f"%{param['var']}%", param['val'])
                for param in params_parsed:
                    rag_query = rag_query.replace(f"%{param['var']}%", param['val'])
                template['slides'][slide_num]['body'][i].prompt = prompt
                template['slides'][slide_num]['body'][i].rag_query = rag_query
                template['slides'][slide_num]['body'][i].params = [{p['var']: p['val']} for p in params_parsed]

        print("fill params done")

        return template

    def get_template_result(self, template: dict) -> dict:

        for (i, slide) in enumerate(template['slides']):
            template = self.__fill_params(template, i)
            header_output = self.__run_component_no_params(slide['header'])
            template['slides'][i]['header'].output = {
                "answer": header_output.answer,
                "transcript": header_output.transcript,
                "params": header_output.params
            }

            for (j, component) in enumerate(slide['body']):
                component_output = self.__run_component_no_params(component)
                template['slides'][i]['body'][j].output = {
                    "answer": component_output.answer,
                    "transcript": component_output.transcript,
                    "params": component_output.params
                }

        return template



haystack_template_processor = HaystackTemplateProcessor()
