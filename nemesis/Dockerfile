FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi==0.115.6 uvicorn==0.34.0 google-cloud-storage==2.19.0
COPY app.py index.html ./
ENV PORT=8080
CMD exec uvicorn app:app --host 0.0.0.0 --port $PORT
