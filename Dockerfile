FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
COPY main.py .
COPY bot_1732123456.session .   # ← PUT YOUR FILE NAME HERE

RUN pip install telethon

CMD ["python", "-u", "main.py"]
