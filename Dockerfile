FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY BuceaSrunLogin ./BuceaSrunLogin
COPY always_online.py .

CMD ["python", "always_online.py"]
