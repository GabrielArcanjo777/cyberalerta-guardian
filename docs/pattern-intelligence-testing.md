# Sprint 25V5 - Pattern Intelligence, Testes e ML Realista

## Objetivo

Pattern Intelligence comeca rule-based, explicavel e testavel. Nao ha treino de modelo,
API externa de IA ou promessa de certeza absoluta.

O servico registra:

- texto normalizado;
- hash do texto normalizado;
- sinais detectados;
- score 0-100;
- clusters simples;
- recorrencia por texto, remetente e pessoa protegida;
- recorrencia por tipo de golpe/padrao;
- feedback humano como ground truth inicial.

## Estruturas V5

- `PatternSignal`: sinal explicavel gerado por regra.
- `PatternRule`: regra com regex, peso, label e explicacao.
- `PatternDetectionResult`: score, nivel, sinais, recorrencia, tipo de golpe e explicacao.
- `PatternCluster`: agrupamento simples por padrao, texto parecido, remetente, pessoa ou tipo.
- `PatternCandidate`: registro preparado para dataset futuro.
- `PatternFeedback`: feedback humano ligado a candidatos.
- `NormalizedThreatText`: texto normalizado, hash, fingerprint e tokens.
- `RiskExplanation`: resumo, motivos, recomendacao e thresholds.

## Regras

- `urgency`
- `pix_or_payment`
- `new_number`
- `suspicious_link`
- `do_not_call`
- `secrecy_request`
- `emotional_pressure`
- `false_relative`
- `fake_support_center`
- `benefit_regularization`
- `code_token`
- `repeated_similar_text`
- `recurring_sender`
- `recurring_protected_person`
- `recurring_threat_type`

## Thresholds

- `low`: abaixo de 25
- `medium`: 25 a 54
- `high`: 55 a 79
- `critical`: 80 ou mais

O score e limitado a 100.

## Feedback

O feedback do responsavel registra:

- `confirmed_scam`
- `false_alarm`
- `needs_review`
- `resolved`

Esse label fica ligado ao `PatternCandidate` e ao `PatternFeedback`, preparando um dataset
futuro para medir falsos positivos, falsos negativos, tipos de golpe recorrentes e sinais mais
frequentes.

## Console

O Guardian Console mostra no detalhe do caso:

- score de padrao;
- nivel;
- tipo de golpe/padrao principal;
- explicacao curta;
- sinais;
- recorrencia;
- clusters;
- evidencias/razoes principais;
- feedback label quando existir.

## Fora do escopo

- ML real.
- Treino de modelo.
- API externa.
- Agentes avancados.
- WhatsApp producao.
- Persistencia fisica.
