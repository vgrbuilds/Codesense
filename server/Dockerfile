# using python 3.12 slim image
FROM python:3.12-slim

# setting python defaults for containers
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# setting the app working directory
WORKDIR /app

# installing uv package manager
RUN pip install --no-cache-dir uv

# copying dependency manifests first for layer caching
COPY pyproject.toml uv.lock ./

# installing project dependencies from lock file
RUN uv sync --frozen --no-dev

# copying the source code
COPY src ./src
COPY API_DOCS.md ./API_DOCS.md
COPY Readme.md ./Readme.md

# exposing the default server port
EXPOSE 8000

# running the fastapi server
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
