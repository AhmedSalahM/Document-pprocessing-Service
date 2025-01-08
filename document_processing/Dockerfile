FROM python:slim
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
copy requirment.txt /code/
RUN pip install --no-cache-dir -r requirment.txt
COPY  . /code/
