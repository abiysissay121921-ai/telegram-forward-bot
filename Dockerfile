FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
COPY main.py .
COPY my_bot.session .

RUN pip install --no-cache-dir telethon

CMD ["python", "-u", "main.py"]
