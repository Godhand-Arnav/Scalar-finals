FROM python:3.11-slim

LABEL maintainer="FORGE Research Team"
LABEL description="FORGE: Forensic RL Graph Environment for Misinformation Investigation"

# ── System dependencies ───────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── Python dependencies (cached layer) ───────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Pre-download embedding model (free, cached in image) ──────────────────────
RUN python -c "from sentence_transformers import SentenceTransformer; \
               SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# ── Application code ──────────────────────────────────────────────────────────
COPY . .

# ── Environment variables (set at runtime, no secrets in image) ───────────────
ENV OPENAI_API_KEY=""
ENV API_BASE_URL="https://api.groq.com/openai/v1"
ENV MODEL_NAME="llama3-8b-8192"
ENV HF_TOKEN=""
ENV SERVER_HOST="0.0.0.0"
ENV SERVER_PORT="7860"

EXPOSE 7860

# ── Healthcheck ───────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# ── Entry point ───────────────────────────────────────────────────────────────
CMD ["uvicorn", "server.main:app", \
     "--host", "0.0.0.0", \
     "--port", "7860", \
     "--workers", "2", \
     "--log-level", "info"]
