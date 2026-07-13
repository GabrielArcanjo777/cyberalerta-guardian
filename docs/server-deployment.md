# Deploy do CyberAlerta Guardian no servidor Linux

Guia do **`compose.server.yml`** — a configuração de produção do piloto, pensada
para rodar atrás de um **Cloudflare Tunnel** num notebook Linux Mint dedicado.

> Este arquivo **não substitui** o `docker-compose.evolution.yml` (dev local).
> Fluxo oficial: código no Windows → push para o GitHub → `git pull` no servidor.

---

## 1. O que sobe

| Serviço     | Imagem                            | Publica no host?            | Rede(s)                          |
|-------------|-----------------------------------|-----------------------------|----------------------------------|
| `frontend`  | build `./frontend` (Next.js)      | **127.0.0.1:3000** (túnel)  | `edge`                           |
| `backend`   | build `./backend` (FastAPI)       | **127.0.0.1:8000** (túnel)  | `edge`, `backend_private`        |
| `postgres`  | `postgres:16-alpine`              | **não**                     | `data_private`                   |
| `redis`     | `redis:7-alpine`                  | **não**                     | `data_private`                   |
| `evolution` | `evoapicloud/evolution-api:v2.3.7`| **não**                     | `backend_private`, `data_private`|
| `n8n`       | `n8nio/n8n:1.66.0` (profile)      | **não** (desligado)         | `backend_private`                |

**Regra de ouro:** só `frontend` e `backend` são publicados, e **apenas em
`127.0.0.1`**. Postgres, Redis, Evolution e a UI do n8n **nunca** são expostos —
o Cloudflare Tunnel conecta somente ao loopback do frontend e do backend.

> O backend usa **SQLite** (volume `/data`). Postgres/Redis atendem a **Evolution**
> hoje (e a futura migração do backend prevista no plano mestre). Não troque
> `STORAGE_BACKEND` para postgres sem suporte no código.

---

## 2. Requisitos

- Linux com Docker Engine + plugin Compose v2 (`docker compose version`).
- ~8 GB RAM (limites de memória já ajustados; ver §9).
- `cloudflared` instalado e um túnel apontando para `127.0.0.1:3000` (app) e
  `127.0.0.1:8000` (API). O túnel termina o TLS — por isso os cookies são `Secure`.
- **SSD** como `data-root` do Docker (ver §8).

---

## 3. Arquivos `.env` necessários

Nada de segredo vai para o Git. No servidor, crie os arquivos reais a partir dos
exemplos versionados:

| Real (servidor, git-ignored) | A partir de              | Quando            |
|------------------------------|--------------------------|-------------------|
| `.env.server`                | `.env.server.example`    | sempre            |
| `.env.n8n`                   | `.env.n8n.example`       | só com profile n8n|

```bash
cp .env.server.example .env.server
# edite .env.server e preencha os segredos (§4)
```

Variáveis **obrigatórias** (o compose falha sem elas):

- `AUTH_SECRET_KEY`
- `EVOLUTION_API_KEY`
- `EVOLUTION_WEBHOOK_SECRET`
- `POSTGRES_PASSWORD`
- `REDIS_PASSWORD`
- `NEXT_PUBLIC_API_URL` (URL pública da API; embutida no build do frontend)

---

## 4. Como gerar segredos

```bash
# Chaves/senhas fortes (rode uma vez por variável):
python3 -c "import secrets; print(secrets.token_urlsafe(48))"   # AUTH_SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"   # EVOLUTION_API_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"   # EVOLUTION_WEBHOOK_SECRET
python3 -c "import secrets; print(secrets.token_urlsafe(32))"   # POSTGRES_PASSWORD
python3 -c "import secrets; print(secrets.token_urlsafe(32))"   # REDIS_PASSWORD
```

Cole cada valor no `.env.server`. **Nunca** comite o `.env.server`. Rotação:
troque o valor, recrie os serviços afetados (`up -d`) e, para o Postgres, atualize
a senha do papel no banco antes de reiniciar a Evolution.

---

## 5. Validar (sem subir nada)

```bash
docker compose --env-file .env.server -f compose.server.yml config
```

Isso resolve as variáveis e valida a sintaxe **sem iniciar contêineres**. Se
faltar um segredo obrigatório, o comando falha citando o nome da variável.

---

## 6. Subir / parar / atualizar / rollback

```bash
# Subir (build das imagens locais na primeira vez)
docker compose --env-file .env.server -f compose.server.yml up -d --build

# Ver estado e saúde
docker compose --env-file .env.server -f compose.server.yml ps

# Parar (mantém volumes/dados)
docker compose --env-file .env.server -f compose.server.yml down

# Atualizar após um git pull
git pull
docker compose --env-file .env.server -f compose.server.yml up -d --build

# Ativar o n8n (opcional) — exige .env.n8n
docker compose --env-file .env.server -f compose.server.yml --profile n8n up -d
```

**Rollback:**

```bash
# Volte o código e rebuilde
git checkout <tag-ou-commit-anterior>
docker compose --env-file .env.server -f compose.server.yml up -d --build
```

Os dados persistem em volumes nomeados; um rollback de código **não** apaga
banco/sessão. Para restaurar dados, use um backup do volume (§8). **Nunca** rode
`down -v` num incidente sem backup — isso remove volumes.

---

## 7. Portas locais e redes

- **Publicado (só `127.0.0.1`):** `3000` (frontend), `8000` (backend).
  Ajuste com `FRONTEND_HOST_PORT` / `BACKEND_HOST_PORT` no `.env.server`.
- **Nunca publicado:** Postgres, Redis, Evolution, n8n.
- **Redes:**
  - `edge` — frontend + backend (camada do túnel).
  - `backend_private` (`internal: true`) — backend ↔ evolution/n8n.
  - `data_private` (`internal: true`) — postgres/redis/evolution; **sem** saída à
    internet nem ao `edge`.

O `backend` NÃO fica na `data_private` (usa SQLite): menor superfície possível.

> Escutar `0.0.0.0` **dentro** dos contêineres (uvicorn/next) é normal e
> necessário para receber tráfego do bridge Docker. A restrição de segurança é a
> **publicação no host**, que é sempre `127.0.0.1:<porta>` — nunca `0.0.0.0`.

---

## 8. Volumes e discos (SSD vs HDD degradado)

Volumes nomeados (gerenciados pelo Docker), **sem caminhos físicos no compose**:

| Volume                | Conteúdo                          | Criticidade |
|-----------------------|-----------------------------------|-------------|
| `backend_data`        | SQLite do backend                 | crítico     |
| `pgdata`              | Postgres (sessão/mensagens)       | crítico     |
| `redisdata`           | Redis (cache/AOF)                 | crítico     |
| `evolution_instances` | Sessão pareada da Evolution       | crítico     |
| `n8n_data`            | Workflows/credenciais do n8n      | crítico     |

**Todos os dados críticos devem ficar no SSD.** Como o compose não fixa caminhos,
garanta isso de uma destas formas:

1. **Recomendado:** aponte o `data-root` do Docker para o SSD
   (`/etc/docker/daemon.json` → `{"data-root": "/caminho/no/ssd/docker"}`,
   depois `systemctl restart docker`). Todos os volumes passam a viver no SSD.
2. Ou relocalize volumes específicos com bind/symlink do diretório do volume.

O **HDD degradado não é requisito** da aplicação. Poderá, no futuro, servir só
para conteúdo descartável (cache, scratch, cópia secundária de backup) — nunca
para Postgres/Redis/Evolution/n8n primários nem para segredos.

**Backup de volume (exemplo, Postgres):**

```bash
docker run --rm -v pgdata:/data -v "$PWD/backups:/backup" alpine \
  tar czf /backup/pgdata-$(date +%F).tgz -C /data .
```

Guarde backups fora do servidor. `backups/` já está no `.gitignore`.

---

## 9. Hardening aplicado

- `restart: unless-stopped`, `init: true`, `stop_grace_period` em todos.
- Healthchecks: backend (`/health`), frontend (home), postgres (`pg_isready`),
  redis (`redis-cli ping`), evolution (HTTP interno).
- Limites de log: `json-file`, `max-size=10m`, `max-file=3`.
- Limites de memória (total com n8n desligado ≈ 3,7 GB; folga para SO + túnel):

  | Serviço   | limite | reserva |
  |-----------|--------|---------|
  | postgres  | 1024M  | 256M    |
  | evolution | 1024M  | 256M    |
  | backend   | 640M   | 192M    |
  | frontend  | 640M   | 192M    |
  | redis     | 384M   | 128M    |
  | n8n       | 512M   | 128M    |

- `security_opt: no-new-privileges:true` em todos.
- `cap_drop: ALL`, `read_only` + `tmpfs`, usuário **não-root**: backend, redis.
  Frontend: não-root + `cap_drop: ALL` + `tmpfs` (sem `read_only`, pois o Next
  grava cache de runtime).
- **Nunca** montamos `/var/run/docker.sock`. **Nenhum** serviço usa `privileged`.

### Exceções documentadas
- **postgres:** só `no-new-privileges`. O entrypoint precisa iniciar como root
  para inicializar/chown o datadir e então baixar privilégios (gosu); `cap_drop:
  ALL`/`read_only`/`user` quebrariam a criação do volume.
- **evolution:** só `no-new-privileges`. Imagem **não oficial** (Baileys);
  evitamos `cap_drop`/`read_only`/`user` para não arriscar a sessão pareada.

---

## 10. Postura de segurança inicial (piloto)

Defaults do `.env.server.example` (mantenha até o checklist de piloto):

```
DRY_RUN=true
BETA_REAL_SEND_ENABLED=false
AUTH_REQUIRE_SENSITIVE_ROUTES=true
STORE_FULL_MESSAGE=false
HYBRID_LLM_SHADOW_MODE=true
```

O **envio real nunca é habilitado por default**. Ligá-lo exige múltiplas
condições independentes (ambiente autorizado, ator autenticado com permissão,
allowlist administrativa, destino ≠ remetente suspeito) — ver a regra cardinal do
plano mestre. Com `APP_ENV=production`, o backend recusa subir sem
`AUTH_SECRET_KEY`, `EVOLUTION_WEBHOOK_SECRET` e `RATE_LIMIT_ENABLED=true`.

**Proibições operacionais:**
- Não publicar Postgres, Redis, Evolution ou a UI do n8n na internet nem em
  `0.0.0.0`. O acesso a eles é só interno (redes privadas) ou via túnel dedicado.
- Não expor a Evolution (canal não oficial) publicamente.
- Não commitar `.env.server`, `.env.n8n`, chaves, backups ou dados de runtime.
