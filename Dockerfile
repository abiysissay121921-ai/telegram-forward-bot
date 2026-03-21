FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
COPY main.py .

RUN pip install -r requirements.txt

CMD ["python", "-u", "main.py"]
