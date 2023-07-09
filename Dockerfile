FROM python:3.7-alpine

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python3", "./server.py", "--bind", "0.0.0.0"]
