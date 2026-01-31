FROM python:3.11-slim

WORKDIR /app

# Ensure Python output is sent straight to terminal (no buffering)
ENV PYTHONUNBUFFERED=1
# Ensure our package is importable as top-level `app` package
ENV PYTHONPATH=/app

# Install system build deps required by some Python packages (asyncpg, cryptography, etc.)
RUN apt-get update \
	&& apt-get install -y --no-install-recommends gcc libpq-dev build-essential curl \
	&& rm -rf /var/lib/apt/lists/*

# install application dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

<<<<<<< HEAD
RUN python -m spacy download pt_core_news_lg
=======
# Install spaCy large language models used by the app
# Install directly from the model release wheels on GitHub (explicit URLs)
RUN pip install --no-cache-dir \
	https://github.com/explosion/spacy-models/releases/download/pt_core_news_lg-3.8.0/pt_core_news_lg-3.8.0-py3-none-any.whl \
	https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl
>>>>>>> 1435e010577676660fffc48990724e8a50c65cb7
# copy application source
COPY . .

EXPOSE 8000

# Run uvicorn pointing at top-level `main:app` which imports `app.api`
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
