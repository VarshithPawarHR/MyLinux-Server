# Use an official Python base image
FROM python:3.10-slim

# Set workdir inside the container
WORKDIR /app

# Copy pyproject.toml & uv.lock (not for pip - pip dont use)
COPY pyproject.toml ./
COPY uv.lock ./

# Install uv
RUN pip install uv

# Install dependencies with uv
RUN uv venv .venv && uv sync

# Caching 
COPY . .

# Use uv's venv as the default Python
ENV PATH="/app/.venv/bin:$PATH"

# Run your monitor.py
CMD ["python", "monitor.py"]
