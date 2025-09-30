FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt /app/
RUN apt-get update && apt-get install -y gcc libpq-dev build-essential && pip install --no-cache-dir -r requirements.txt && apt-get remove -y gcc build-essential && rm -rf /var/lib/apt/lists/*
COPY . /app
EXPOSE 8000
CMD ["uvicorn","all:app","--host","0.0.0.0","--port","8000","--reload"]
