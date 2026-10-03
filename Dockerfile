FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY provincia_api ./provincia_api

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
