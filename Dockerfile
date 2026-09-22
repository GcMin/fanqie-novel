FROM mcr.microsoft.com/playwright/python:v1.55.0-noble
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends git fonts-noto-cjk && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt && \
    useradd --create-home --uid 10001 publisher && \
    mkdir /data && chown publisher:publisher /data
COPY publisher ./publisher
COPY config/publisher.yaml ./config/publisher.yaml
USER publisher
ENTRYPOINT ["python", "-m", "publisher"]
CMD ["watch"]
