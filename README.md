# CyberAlerta Guardian

**Slogan:** Antes do Pix. Antes do clique. Antes do prejuizo.

CyberAlerta Guardian é um projeto de intervenção pre-dano para golpes digitais, focado em proteger pessoas vulneráveis antes que um pagamento ou ação maliciosa seja concluída.

Status: Sprints 18A–18G — proteção assistida (demo MVP)

## Demo principal recomendada

Apresente o fluxo completo de proteção assistida na rota:

**[/assisted-demo](http://localhost:3000/assisted-demo)** (com `npm run dev` no frontend)

Roteiro de apresentação: [docs/assisted-protection-demo-script.md](docs/assisted-protection-demo-script.md)

Fluxo: mensagem suspeita → canal simples → resposta curta → Guardian Console → Trust Lock → Trusted Circle (simulado) → Proof of Trust → Agent Decision Trace → relatório.

Stack planejada:
- FastAPI
- Next.js
- TypeScript
- Tailwind

Próximas sprints:
- Sprint 1 Backend
- Sprint 2 Frontend
- Sprint 3 Integracao
- Sprint 4 Agent Decision Trace
- Sprint 5 Family Console
- Sprint 6 Recovery
- Sprint 7 Dashboard
- Sprint 8 Docs
- Sprint 9 Deploy/Submissao
