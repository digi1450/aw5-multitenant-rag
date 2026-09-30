FROM python:3.14-slim
WORKDIR /app
COPY aw5_backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY aw5_backend /app/aw5_backend
CMD ["python", "-m", "aw5_backend.api"]
