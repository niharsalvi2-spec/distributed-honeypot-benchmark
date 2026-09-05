FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "collectors.raw_ingestion.http_ingestor:app", "--host", "0.0.0.0", "--port", "8000"]
