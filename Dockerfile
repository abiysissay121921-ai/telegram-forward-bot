FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
COPY main.py .
COPY session_1732123456.session .   # ← CHANGE THIS TO YOUR FILE NAME

RUN pip install telethon

CMD ["python", "-u", "main.py"]
