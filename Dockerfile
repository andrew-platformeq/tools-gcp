# Pinned by digest for reproducible builds. Update when rebuilding base image.
FROM python:3.11-slim-bookworm@sha256:4740c55e5718c9181cd9cbfa1e13a0c045185ddcf748d6e7a49b3442faec1a53

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Non-root user — Cloud Run does not require root.
RUN groupadd --gid 1000 tools && \
    useradd --uid 1000 --gid tools --shell /bin/bash --create-home tools

COPY pyproject.toml requirements.txt ./
COPY src/ ./src/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir . && \
    chown -R tools:tools /app

USER tools

EXPOSE 8080

CMD ["tools-serve"]
