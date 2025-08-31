FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update -y && apt-get install -y --no-install-recommends \
	ca-certificates \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app /app/app
COPY web /app/web

ENV PORT=8000 HOST=0.0.0.0

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
