FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.lock /app/backend/requirements.lock
RUN pip install --no-cache-dir -r backend/requirements.lock
COPY . /app
ENV AE_DB=/data/ae-prepware.sqlite
EXPOSE 8501
CMD ["uvicorn", "online:app", "--host", "0.0.0.0", "--port", "8501", "--workers", "1"]
