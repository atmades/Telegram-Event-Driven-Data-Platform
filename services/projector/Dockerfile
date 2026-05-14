FROM python:3.11-slim

WORKDIR /app

COPY services/projector/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/projector/app ./app
COPY shared ./shared

CMD ["python", "-m", "app.main"]