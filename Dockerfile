FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .
COPY final_bot.session .

# Run with unbuffered output and longer timeout
CMD ["python", "-u", "main.py"]
