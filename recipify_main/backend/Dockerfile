FROM python:3.10.6
#FROM tensorflow/tensorflow:2.10.0
COPY . .
COPY requirements.txt requirements.txt
#COPY setup.py /setup.py
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD uvicorn api.fast:app --port=$PORT --host=0.0.0.0
