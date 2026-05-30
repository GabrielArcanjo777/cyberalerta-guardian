# CyberAlerta Guardian Backend

Este backend é parte do CyberAlerta Guardian, um sistema agentic de intervenção pre-dano contra golpes digitais.

## Instalação

1. Acesse a pasta `backend`:
   ```bash
   cd backend
   ```
2. Crie um ambiente virtual Python e ative:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Como rodar

```bash
uvicorn main:app --reload
```

## Endpoints

- `GET /health` - verifica se o serviço está ativo.
- `GET /examples` - retorna cenários de golpe de exemplo.
- `POST /analyze` - analisa um caso de possível golpe e retorna decisão do agente.
- `POST /recovery` - gera checklist de recuperação condicional.
- `POST /report` - recebe análise e retorna relatório estruturado.

## Exemplos curl

```bash
curl http://localhost:8000/health
```

```bash
curl http://localhost:8000/examples
```

```bash
curl -X POST http://localhost:8000/analyze -H "Content-Type: application/json" -d @payload.json
```

## Agentes implementados

- IntentDetectionAgent
- ManipulationAnalysisAgent
- ScamStageAgent
- ScamClassificationAgent
- RiskScoringAgent
- TrustEvidenceAgent
- TrustLockAgent
- ProofOfTrustAgent
- InterventionPlaybookAgent
- TrustedCircleAgent
- RecoveryAgent
- ReportAgent
- SafetyPolicyService

## Testes

```bash
pytest
```
