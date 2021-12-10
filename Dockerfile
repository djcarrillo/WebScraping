FROM python:3.9

RUN mkdir project
COPY . project/
WORKDIR project/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN ["python3"]