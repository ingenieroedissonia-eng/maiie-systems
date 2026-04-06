# ---------------------------------------------------------
# MAIIE SYSTEM V2
# Docker Container Configuration
# Registro 23
# ---------------------------------------------------------
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN mkdir -p /app/output
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080
ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
