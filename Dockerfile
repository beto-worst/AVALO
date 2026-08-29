FROM python:3.9
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
RUN apt-get update && apt-get install -y libreoffice-core libreoffice-common libreoffice-writer default-jre tesseract-ocr tesseract-ocr-spa

EXPOSE 443 

CMD ["python", "manage.py", "runserver", "0.0.0.0:8800"]
