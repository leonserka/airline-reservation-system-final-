FROM python:3.11-slim

RUN apt-get update && apt-get install -y wget unzip && \
    wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-stable-linux-amd64.zip && \
    unzip ngrok-stable-linux-amd64.zip -d /usr/local/bin && \
    rm ngrok-stable-linux-amd64.zip

RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "airline_reservation_django/manage.py", "runserver", "0.0.0.0:8000"]

ENV PYTHONDONTWRITEBYTECODE=1
