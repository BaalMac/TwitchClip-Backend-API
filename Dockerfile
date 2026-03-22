FROM python:3.12-slim

WORKDIR /TwitchClip-Backend-API

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

RUN mkdir -p logs

ENV PORT=5000
EXPOSE 5000

CMD ["python3", "run.py" ]