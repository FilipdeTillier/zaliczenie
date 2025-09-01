FROM python:3.10-slim


WORKDIR /app

# RUN  pip install --upgrade pip

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create a non-root user and switch to it
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

# Use uvicorn with reload for hot reload functionality
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--reload", "--reload-dir", "/app"]