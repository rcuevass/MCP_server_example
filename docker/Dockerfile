FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY README.md .
COPY src/ src/

RUN pip install -e .

RUN mkdir -p data logs

RUN groupadd -r mcp && useradd -r -g mcp -d /app -s /bin/bash mcp
RUN chown -R mcp:mcp /app
USER mcp

ENV MCP_BASE_DIR=/app \
    MCP_LOG_LEVEL=INFO \
    MCP_TRANSPORT=stdio

CMD ["python", "-m", "mcp_research_server"]
