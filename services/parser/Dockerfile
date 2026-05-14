FROM python:3.11-slim

WORKDIR /app

COPY services/parser/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/parser/app ./app
COPY services/parser/tests ./tests
COPY shared ./shared

CMD ["python", "-m", "app.main"]