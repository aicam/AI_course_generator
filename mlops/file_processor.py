import PyPDF2
import shutil
import os

from . import TEMP_PATH, TEMP_PROCESSED_PATH, DELIMITER
from .haystack_adopter import haystack_adopter


class FileProcessor:

    def __init__(self):
        self.tmp_path = TEMP_PATH
        self.tmp_processed_path = TEMP_PROCESSED_PATH
        self.name_delimiter = DELIMITER

    def pdf_to_txt(self, pdf_path, file_txt_path):
        with open(pdf_path, 'rb') as file:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)

            # Check if PDF is encrypted
            if pdf_reader.is_encrypted:
                pdf_reader.decrypt('')

            # store whole file
            doc_txt = ""

            # Extract text from each page
            total_page_num = len(pdf_reader.pages)

            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                doc_txt += ' ' + text

            with open(file_txt_path, 'w') as processed_f:
                processed_f.write(text)
                processed_f.close()



    def write_file_in_tmp(self, f: str, f_path: str) -> None:
        with open(f_path, "wb") as destination:
            for chunk in f.chunks():
                destination.write(chunk)
            destination.close()

    def get_doc_name(self, name: str) -> str:
        name_txt = ''
        if name[-4:] == '.pdf':
            name_txt = name[:-4] + '.txt'
        if name[-4:] == '.doc' or name[-5:] == '.docx':
            name_txt = name[:-4] + '.txt' if name[-4:] == '.doc' else name[:-5] + '.txt'
        if name[-4:] == '.txt':
            name_txt = name
        return name_txt

    def process_files(self, files):

        if not os.path.exists(self.tmp_path):
            os.mkdir(self.tmp_path)
        if not os.path.exists(self.tmp_processed_path):
            os.mkdir(self.tmp_processed_path)

        for filename, file in files.items():
            name = files[filename].name
            name_txt = self.get_doc_name(name)
            file_path = self.tmp_path + f"/{name}"
            file_txt_path = self.tmp_processed_path + f"/{name_txt}"
            self.write_file_in_tmp(files[filename], file_path)

            # self.pdf_to_txt(file_path, file_txt_path)

        haystack_adopter.process_dir("test")

        # shutil.rmtree(self.tmp_path, ignore_errors=True)
        # shutil.rmtree(self.tmp_processed_path, ignore_errors=True)


file_processor = FileProcessor()