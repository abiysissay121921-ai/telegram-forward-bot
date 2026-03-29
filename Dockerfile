FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir telethon

COPY main.py .
COPY final_bot.session .

CMD ["python", "-u", "main.py"]
