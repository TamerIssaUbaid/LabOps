
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

RUN useradd --system --no-create-home appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

CMD ["python", "app.py"]
