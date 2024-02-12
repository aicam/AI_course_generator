FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

RUN apt-get update && apt-get install -y python3.11-dev \
    libxml2-dev \
    libxslt1-dev \
    antiword \
    unrtf \
    poppler-utils \
    tesseract-ocr \
    flac \
    ffmpeg \
    lame \
    libmad0  \
    libsox-fmt-mp3  \
    sox  \
    libjpeg-dev  \
    swig

# Install dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt
RUN apt-get install wkhtmltopdf -y

# Copy the project code into the container
COPY . /app/