# Built from the repo root (docker-compose.yml): the Art Department borrows Sheets' image calls.
FROM python:3.12-slim
WORKDIR /app
COPY sheets/sheets.py sheets/steps.txt sheets/steps-place.txt /app/sheets/
COPY art/server.py art/art.html /app/art/
ENV SHEETS_CODE=/app/sheets ART_DIR=/app/art/data SECRETS_FILE=/app/secrets/keys.json PORT=8002
EXPOSE 8002
CMD ["python3", "art/server.py"]
