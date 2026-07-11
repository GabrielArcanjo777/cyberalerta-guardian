# Métricas v1 — detector determinístico (dataset sintético)

Gerado em 2026-07-11 11:53Z por `backend/scripts/evaluate_dataset.py` (código de produção real,
sem LLM — postura padrão). Dataset: `backend/data/scam_dataset_v1.jsonl`,
**305 mensagens** (150 golpe / 155 legítimas), sintético e rotulado
à mão (ver provenance em `backend/scripts/dataset_v1.py`).

## 1. Alerta ao contato de confiança (regra atual: risco HIGH, score ≥ 65)

| TP | FP | FN | TN | Precisão | Recall | FPR | F1 |
|---|---|---|---|---|---|---|---|
| 15 | 0 | 135 | 155 | 100.0% | 10.0% | 0.0% | 18.2% |


Interpretação: das mensagens que disparariam alerta, 100.0% são golpe
de verdade; o detector captura 10.0% dos golpes; 0.0% das
mensagens legítimas gerariam alerta indevido.

## 2. Criação de caso no console (score ≥ 40)

| TP | FP | FN | TN | Precisão | Recall | FPR | F1 |
|---|---|---|---|---|---|---|---|
| 87 | 3 | 63 | 152 | 96.7% | 58.0% | 1.9% | 72.5% |


Casos MEDIUM não alertam ninguém — ficam no Guardian Console para revisão. FPR maior
aqui é esperado e aceitável (custo = revisão humana, não incômodo à família).

## 3. Policy Engine híbrida SEM LLM (postura padrão segura)

Com `HYBRID_REQUIRE_LLM_FOR_AUTO_ALERT=true` e LLM indisponível, o máximo é REVIEW
(nunca AUTO_ALERT) — comportamento verificado:

| Label | DISCARD | REVIEW | AUTO_ALERT |
|---|---|---|---|
| golpe (n=150) | 26 | 124 | 0 |
| legítima (n=155) | 97 | 58 | 0 |

## Falsos negativos do alerta (golpes com score < 65)

- `s003` [FAMILY_IMPERSONATION] score=45 sinais=pix_or_payment,new_number — “Pai, e o Lucas. Meu chip queimou, esse e meu numero novo. Preciso pagar um boleto hoje, me”
- `s004` [FAMILY_IMPERSONATION] score=45 sinais=urgency,do_not_call — “Vo, sou seu neto. Estou com um problema serio e preciso de dinheiro agora. Nao liga pro me”
- `s005` [FAMILY_IMPERSONATION] score=60 sinais=pix_or_payment,new_number,emotional_pressure — “Amor, troquei de numero, salva esse. Preciso muito de um favor, faz um pix de 350 pra essa”
- `s006` [FAMILY_IMPERSONATION] score=25 sinais=pix_or_payment — “Tia, meu telefone molhou, to usando esse provisorio. A senhora consegue fazer uma transfer”
- `s007` [FAMILY_IMPERSONATION] score=45 sinais=urgency,pix_or_payment — “Mae, nao conta pro pai, mas preciso de 500 reais urgente. Faz o pix nessa chave que te man”
- `s011` [FAMILY_IMPERSONATION] score=25 sinais=pix_or_payment — “Filha, e o papai. Perdi o celular e to no numero de um amigo. Me manda um pix de 300 que d”
- `s012` [FAMILY_IMPERSONATION] score=40 sinais=urgency,new_number — “Oi vo, mudei de numero. Nao fala com ninguem sobre isso, mas to devendo uma pessoa perigos”
- `s013` [FAMILY_IMPERSONATION] score=60 sinais=urgency,pix_or_payment,emotional_pressure — “Mana, meu celular pifou. Me empresta 450 no pix ate sexta? E urgente, confia em mim.”
- `s014` [FAMILY_IMPERSONATION] score=20 sinais=urgency — “Oi mae, to escrevendo do numero da minha colega. Preciso que transfira 900 agora pra nao p”
- `s015` [FAMILY_IMPERSONATION] score=50 sinais=pix_or_payment,do_not_call — “Pai, troquei de chip. Faz um favor: paga esse boleto de 780 hoje que amanha te devolvo, na”
- `s017` [FAMILY_IMPERSONATION] score=60 sinais=urgency,pix_or_payment,emotional_pressure — “Mae, sou eu. Emprestaram esse celular pra mim. Caiu minha venda e preciso pagar o forneced”
- `s018` [FAMILY_IMPERSONATION] score=40 sinais=urgency,new_number — “Vozinha, e o Pedrinho. Troquei de numero. Nao conta pra mamae, mas preciso de uma grana ur”
- `s019` [FAMILY_IMPERSONATION] score=45 sinais=urgency,pix_or_payment — “Amor, esse e meu numero temporario. Me faz um pix de 200 agora que meu cartao bloqueou e t”
- `s021` [FAMILY_IMPERSONATION] score=45 sinais=urgency,pix_or_payment — “Mae, meu whats antigo foi hackeado, usa so esse. Preciso que faca uma transferencia agora,”
- `s022` [FAMILY_IMPERSONATION] score=60 sinais=pix_or_payment,new_number,emotional_pressure — “E o Joao, primo da Renata. To com numero novo. Consegue me adiantar 350 no pix hoje? E eme”
- … e mais 120

## Falsos positivos do alerta (legítimas com score ≥ 65)

- (nenhum)

## Falsos positivos de caso (legítimas com score ≥ 40 → console)

- `l011` [pix_legit] score=45 sinais=urgency,pix_or_payment — “O condominio agora aceita pix, bem mais facil que boleto.”
- `l030` [payment_legit] score=45 sinais=urgency,pix_or_payment — “Vou pagar a metade da viagem agora e o resto em janeiro, combinado com a agencia.”
- `l078` [link_benign] score=40 sinais=urgency,unknown_link — “O grupo da familia agora tem link de convite, te mandei no privado.”

## Limitações (honestas)

- Dataset **sintético** escrito à mão; não substitui mensagens reais de piloto.
- Métricas medem apenas a camada **determinística** (regex + pesos). A análise LLM
  do pipeline híbrido não entra aqui — exige provider real; o desenho previsto é
  rodá-la em **shadow mode** durante o piloto e comparar as decisões gravadas.
- Sem near-duplicates/augmentation: cada linha é uma mensagem distinta.
- Rotulagem por um único autor; sem validação cruzada de anotadores.
