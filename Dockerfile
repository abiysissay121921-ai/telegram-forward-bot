FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install requirements
RUN pip install --no-cache-dir telethon

# Copy the bot code
COPY main.py .

# Run the bot
CMD ["python", "main.py"]
