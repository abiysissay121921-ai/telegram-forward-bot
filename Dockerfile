FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
COPY main.py .
COPY bot_final_2026.session .

RUN pip install telethon

CMD ["python", "-u", "main.py"]
