import base64

import PyPDF2
import boto3
import shutil
from pdf2image import convert_from_path
import os
from django.utils.datastructures import MultiValueDict

from . import TEMP_PATH, TEMP_PROCESSED_PATH, DELIMITER
from .haystack_adopter import haystack_adopter


class FileProcessor:

    def __init__(self, s3_base_url: str, s3_directory: str):
        self.tmp_path = TEMP_PATH
        self.tmp_processed_path = TEMP_PROCESSED_PATH
        self.name_delimiter = DELIMITER
        self.index_name = "test"
        self.s3_base_url = s3_base_url
        self.s3_directory = s3_directory

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



    def write_file_in_tmp(self, f, f_path: str) -> None:
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

    def process_files(self, files: MultiValueDict):

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

            self.pdf_to_txt(file_path, file_txt_path)

        haystack_adopter.process_dir(self.index_name)

        shutil.rmtree(self.tmp_path, ignore_errors=True)
        shutil.rmtree(self.tmp_processed_path, ignore_errors=True)

    def upload_file_s3(self, file_path: str, file_name: str):
        s3_client = boto3.client('s3')
        try:
            s3_client.upload_file(file_path, os.environ["AWS_STORAGE_BUCKET_NAME"], self.s3_directory + file_name)
        except Exception as e:
            return e
        return None

    def pdf2img(self, path):
        try:
            images = convert_from_path(path)
            num_pages = len(images)
            for (i, img) in enumerate(images):
                img.save(f'{self.tmp_processed_path}/page-{i}.jpg', 'JPEG')
        except Exception as e:
            return 0, e
        else:
            return num_pages, None

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def process_images(self, files: MultiValueDict):

        if not os.path.exists(self.tmp_path):
            os.mkdir(self.tmp_path)
        if not os.path.exists(self.tmp_processed_path):
            os.mkdir(self.tmp_processed_path)

        for filename, file in files.items():
            name = files[filename].name
            file_path = self.tmp_path + f"/{name}"
            self.write_file_in_tmp(files[filename], file_path)

            num_pages, err = self.pdf2img(self.tmp_path + name)
            if err is not None:
                return [], err

            image_urls = []
            for i in range(num_pages):
                # self.upload_file_s3(self.tmp_processed_path + f"page-{i}.jpg", f"page-{i}.jpg")
                base64_image = self.encode_image(self.tmp_processed_path + f"page-{i}.jpg")
                image_urls.append(f"data:image/jpeg;base64,{base64_image}")

            shutil.rmtree(self.tmp_path, ignore_errors=True)
            shutil.rmtree(self.tmp_processed_path, ignore_errors=True)

            return image_urls, err


file_processor = FileProcessor(os.environ['AWS_S3_BASE_URL'], os.environ['AWS_S3_BASE_DIRECTORY'])