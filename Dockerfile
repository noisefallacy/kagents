FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8000
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /app

COPY requirements.txt pyproject.toml README.md ./
COPY src ./src
COPY agents ./agents
COPY data ./data
COPY prompts ./prompts
COPY docs ./docs
COPY outputs/.gitkeep ./outputs/.gitkeep
COPY outputs/browser/.gitkeep ./outputs/browser/.gitkeep

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt \
    && python -m pip install --no-cache-dir -e . --no-build-isolation \
    && python -m playwright install --with-deps chromium

EXPOSE 8000

CMD ["uvicorn", "agents.portfolio_manager.server:app", "--host", "0.0.0.0", "--port", "8000"]
