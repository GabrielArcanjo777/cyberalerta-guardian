# CyberAlerta Guardian — backend FastAPI (imagem de servidor).
# Build reproduzível, usuário não-root, sem segredos embutidos.
# O SQLite de runtime fica num volume montado em /data (ver compose.server.yml).
#
# Build:  docker build -t cyberalerta-backend ./backend
# Uvicorn escuta 0.0.0.0:8000 DENTRO do container (necessário para receber
# tráfego do bridge Docker); a exposição no host é limitada a 127.0.0.1 pelo
# compose. Ver docs/server-deployment.md.

FROM python:3.13-slim AS base

# Não gerar .pyc e não bufferizar stdout/stderr (logs imediatos).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dependências primeiro (camada cacheável). Só runtime — não instala dev deps.
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

# Código da aplicação. main.py fica na raiz de /app (uvicorn main:app).
COPY . .

# Usuário não-root + diretório de dados gravável (volume monta por cima).
RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /data \
    && chown -R appuser:appuser /data /app
USER appuser

# STORAGE_BACKEND/SQLITE_DATABASE_URL vêm do .env; o default aponta para /data
# (volume persistente). Não colocamos segredos aqui.
ENV STORAGE_BACKEND=sqlite \
    SQLITE_DATABASE_URL=sqlite:////data/cyberalerta_guardian.db

EXPOSE 8000

# Healthcheck bate no /health interno (endpoint público de saúde já existente).
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4).status==200 else 1)"

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
