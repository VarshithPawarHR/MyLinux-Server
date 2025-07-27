# Use an official Python base image
FROM python:3.10-slim

WORKDIR /app

# Copy only requirements.txt first for layer caching
COPY requirements.txt .

# Install dependencies globally (inside container)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code
COPY . .

# Run your monitor.py
CMD ["python", "monitor.py"]
