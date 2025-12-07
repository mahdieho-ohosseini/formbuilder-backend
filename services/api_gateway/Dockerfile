FROM python:3.12

WORKDIR /app

COPY . .

RUN pip install fastapi uvicorn httpx python-jose

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7000"]
