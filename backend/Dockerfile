FROM auron-sms-based

WORKDIR /app

COPY backend/. /app
COPY backend/lib/. /usr/local/lib/python3.10/site-packages/pyreportjasper/libs/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]