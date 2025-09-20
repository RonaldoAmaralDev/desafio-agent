FROM python:3.11-slim

WORKDIR /app

COPY fastapi_app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services /app/services
COPY fastapi_app/main.py .

ENV OPENAI_API_KEY=${OPENAI_API_KEY}

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
