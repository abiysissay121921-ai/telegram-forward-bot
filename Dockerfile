FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
COPY main.py .
COPY my_new_bot.session .

RUN pip install telethon

CMD ["python", "-u", "main.py"]
