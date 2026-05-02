FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

RUN chown -R appuser:appgroup /app
USER appuser

# Exposes service port 8010 for the LangGraph Agent API.
EXPOSE 8010

# Health check endpoint: GET / on port 8010.

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8010"]
