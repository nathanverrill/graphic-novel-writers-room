FROM python:3.12-slim
WORKDIR /app
COPY sheets.py server.py steps.txt README.md /app/sheets/
ENV SHEETS_DIR=/app/sheets/characters MD_DIRS=/app/campaigns SECRETS_FILE=/app/secrets/keys.json PORT=8001
EXPOSE 8001
CMD ["python3", "sheets/server.py"]
