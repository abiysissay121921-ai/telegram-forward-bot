FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
COPY main.py .
COPY mysession.session .   # <-- correct spelling, no extra 'e'
RUN pip install --no-cache-dir telethon
CMD ["python", "-u", "main.py"]
