# Auditoria de qualidade e segurança

Revisão executada em 18 de agosto de 2026 sobre o backend FastAPI, o frontend Next.js e a automação de CI. O objetivo foi separar defeitos confirmados de sugestões puramente estilísticas e registrar os riscos que ainda precisam de trabalho.

## Resultado executivo

- Dependências Python: **0 vulnerabilidades conhecidas** em `pip-audit`.
- Dependências npm: **0 vulnerabilidades conhecidas** após atualização e novo lockfile.
- Backend: **360 testes aprovados** após a inclusão de um caso de regressão para o classificador.
- Frontend: lint, TypeScript e build de produção aprovados.
- CI: passa a bloquear novas vulnerabilidades de severidade alta nas dependências Python e npm.

## Correções aplicadas

| Área | Problema confirmado | Correção |
| --- | --- | --- |
| Dependências | Versões vulneráveis de Next.js/PostCSS e pacotes transitivos | Atualização das versões diretas e regeneração do lockfile; auditoria completa zerada. |
| Testes de segurança | `pytest.fail` era usado sem importar `pytest` | Importação explícita, evitando `NameError` justamente nos caminhos de falha. |
| Classificador | Conjunto mutável compartilhado na classe e condição aninhada | Vocabulário imutável com `ClassVar[frozenset]` e regras nomeadas (`involves_family`, `involves_payment`). |
| Navegação | Uso de `window.location.assign` para rota interna | Navegação pelo router do Next.js, preservando o comportamento de aplicação cliente. |
| Fingerprint | SHA-1 reportado como risco criptográfico embora usado apenas como identificador compatível | Uso explicitamente não criptográfico (`usedforsecurity=False`) e documentação da restrição. |
| Configuração | Ternário redundante na proteção de rotas sensíveis | Expressão booleana direta, mantendo o mesmo comportamento. |
| Prevenção | Auditorias eram manuais | Job de segurança no GitHub Actions com `pip-audit` e `npm audit`. |

## Evidências reproduzíveis

```bash
# Backend
python -m pytest backend/app/tests -q
pip-audit -r backend/requirements.txt

# Frontend
cd frontend
npm audit --audit-level=high
npm run lint
npx tsc --noEmit
npm run build
```

## Riscos remanescentes

Estes pontos não foram mascarados como “corrigidos”; exigem mudanças maiores e devem ser tratados em PRs menores e independentes:

1. `frontend/lib/api.ts`, `frontend/lib/types.ts`, `GuardianAdminConsole.tsx` e serviços centrais do backend concentram responsabilidades demais. A divisão deve respeitar contratos existentes e receber testes antes de cada extração.
2. O relatório amplo do Ruff inclui dívida de imports, tipagem e modernização. Uma correção automática em massa produziria um diff de alto risco; a adoção deve ser incremental por módulo, com uma baseline explícita.
3. Há blocos genéricos de `except Exception` em integrações externas. Eles precisam ser refinados por fronteira, preservando logs e políticas de fallback.
4. Rate limiting e idempotência continuam em memória e não funcionam de forma distribuída.
5. O isolamento multi-tenant ainda não cobre todas as entidades, conforme registrado no README e na arquitetura.
6. Integrações externas com URLs fixas e nomes internos de tabelas foram revisadas como superfícies controladas, mas continuam merecendo testes de contrato e validação defensiva antes de produção.

## Critério de Clean Code adotado

Nesta revisão, Clean Code significa reduzir estado mutável, nomear decisões de domínio, simplificar fluxo de controle, usar APIs do framework e garantir regressões com testes. Alterações cosméticas em massa foram evitadas porque aumentariam o risco sem corrigir comportamento.
