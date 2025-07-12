FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

ENV GIT_TERMINAL_PROMPT=0
RUN apt-get update && apt-get install -y curl git && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
