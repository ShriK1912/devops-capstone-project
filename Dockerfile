FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home appuser

COPY service ./service
COPY wsgi.py .

USER appuser

EXPOSE 8080

CMD ["python", "wsgi.py"]
