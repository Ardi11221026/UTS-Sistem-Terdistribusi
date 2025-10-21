FROM python:3.11-slim

WORKDIR /app
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
USER appuser
COPY src/ ./src/
EXPOSE 8080
ENV DEDUP_DB=/app/data/dedup.db
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]
