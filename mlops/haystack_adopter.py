import os

from . import TEMP_PROCESSED_PATH
from haystack.utils import convert_files_to_docs
from haystack.nodes import PreProcessor
from haystack.document_stores import OpenSearchDocumentStore
from haystack.nodes import EmbeddingRetriever, PromptNode

MDDEL = "gpt-4-1106-preview"
class HaystackAdopter:
    '''
    This class provide functionalities using Haystack library to other methods.
    '''

    def __init__(self, os_endpoint: str, os_username: str, os_password: str, os_port: str, openai_api_key: str, preprocessed_dir: str):
        self.os_endpoint = os_endpoint
        self.os_username = os_username
        self.os_password = os_password
        self.os_port = os_port
        self.openai_api_key = openai_api_key
        self.preprocessed_dir = preprocessed_dir

    def get_document_store(self, index_name: str) -> OpenSearchDocumentStore:
        '''
        Connect to OpenSearch and create a document store
        :param index_name: index name in which data is stored or want to be stored
        :return: A Haystack document store object
        '''
        return OpenSearchDocumentStore(
            host=self.os_endpoint,
            port=self.os_port,
            username=self.os_username,
            password=self.os_password,
            similarity="cosine",
            embedding_dim=1536,
            index=index_name)

    def get_retriever(self, document_store: OpenSearchDocumentStore) -> EmbeddingRetriever:
        '''
        Create a retriever based on an embedding model and connect it to a document store
        to update document store or retriever from document store using embedding similarity
        :param document_store: OpenSearched document store instance
        :return: An embedding retriever attached to OpenSearch document store
        '''
        return EmbeddingRetriever(
            document_store=document_store,
            batch_size=128,
            embedding_model="text-embedding-ada-002",
            api_key=self.openai_api_key,
            max_seq_len=1024
        )

    def process_dir(self, index_name: str) -> None:
        '''
        Haystack can aoutomatically parse files inside a folder. This method
        - convert all txt files in a doc into arrays of sentences
        - store them in OpenSearch document store
        - update the document store and replace strings with embeddings
        :param index_name: index name of OpenSearch
        '''
        docs = convert_files_to_docs(TEMP_PROCESSED_PATH, split_paragraphs=True)
        preprocessor = PreProcessor(
            clean_empty_lines=True,
            clean_whitespace=True,
            clean_header_footer=True,
            split_by="word",
            split_length=100,
            split_overlap=10,
            split_respect_sentence_boundary=True,
        )
        processed_docs = preprocessor.process(docs)
        document_store = self.get_document_store(index_name)
        document_store.write_documents(processed_docs)
        retriever = self.get_retriever(document_store)
        document_store.update_embeddings(retriever=retriever)

    def get_prompt_node(self):
        '''
        :return: creates a generic prompt node which is in fact an API call to ChatGPT
        '''
        return PromptNode(MDDEL, api_key=self.openai_api_key)



haystack_adopter = HaystackAdopter(
    os_endpoint=os.environ['OS_ENDPOINT'],
    os_username=os.environ['OS_USERNAME'],
    os_password=os.environ['OS_PASSWORD'],
    os_port=os.environ['OS_PORT'],
    openai_api_key=os.environ['OPENAI_API_KEY'],
    preprocessed_dir='./mlops/tmp_processed/',
)