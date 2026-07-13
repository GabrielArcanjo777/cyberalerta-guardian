# CyberAlerta Guardian — frontend Next.js (imagem de servidor).
# Build multi-stage, usuário não-root. Sem segredos: a única variável de build
# é NEXT_PUBLIC_API_URL (URL PÚBLICA da API, não sensível), embutida no bundle.
#
# IMPORTANTE: NEXT_PUBLIC_* é resolvido em BUILD. Trocar a URL da API exige
# rebuild da imagem. Ver docs/server-deployment.md.

# ---- Stage 1: build -------------------------------------------------------
FROM node:20-alpine AS builder
WORKDIR /app

# Instala dependências de forma determinística a partir do lockfile.
COPY package.json package-lock.json ./
RUN npm ci

# URL pública da API (ex.: https://api.seu-dominio). Default local para dev.
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL} \
    NEXT_TELEMETRY_DISABLED=1

COPY . .
RUN npm run build

# ---- Stage 2: runner ------------------------------------------------------
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000

# Copia apenas o necessário para `next start`, com dono não-root (usuário `node`
# já existe na imagem oficial). .next contém o build; node_modules o runtime.
COPY --chown=node:node --from=builder /app/node_modules ./node_modules
COPY --chown=node:node --from=builder /app/.next ./.next
COPY --chown=node:node --from=builder /app/public ./public
COPY --chown=node:node --from=builder /app/package.json ./package.json
COPY --chown=node:node --from=builder /app/next.config.js ./next.config.js

USER node

EXPOSE 3000

# Healthcheck usa fetch nativo do Node 20 contra a home.
HEALTHCHECK --interval=30s --timeout=5s --start-period=25s --retries=3 \
    CMD node -e "fetch('http://127.0.0.1:3000/').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"

CMD ["npm", "run", "start"]
