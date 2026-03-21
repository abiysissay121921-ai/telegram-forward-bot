FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
COPY main.py .
COPY bot_1774085071 (1).session .

RUN pip install telethon

CMD ["python", "-u", "main.py"]
