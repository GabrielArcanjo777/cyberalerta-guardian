# UX Writing Guidelines

Guia de linguagem para mensagens do CyberAlerta Guardian em demo, WhatsApp/n8n e interfaces operacionais.

## Principios

- Seja claro, calmo e acionavel.
- Diga o que a pessoa deve fazer agora.
- Explique o motivo em uma frase curta.
- Evite promessa de certeza absoluta.
- Evite juridiquês, termos bancarios complexos e linguagem alarmista.
- Nunca peça senha, codigo, token, documento, dado bancario ou comprovante sensivel pelo chat.
- Para risco alto ou critico, oriente pausa antes de Pix, clique, instalacao de app ou envio de codigo.
- Para risco baixo ou medio, oriente verificacao sem bloquear a pessoa de forma dramatica.

## Termos de Produto

| Termo interno | Termo para usuario |
| --- | --- |
| Trust Lock | Bloqueio de Confianca |
| Proof of Trust | Confirmacao Segura |
| Trusted Circle | Contato de Confianca |
| Agent Decision Trace | Por que o sistema recomendou isso |
| Recovery Mode | Modo de Recuperacao |

## Tom por Nivel de Risco

| Risco | Tom | Acao principal |
| --- | --- | --- |
| Baixo | Preventivo | Conferir com calma antes de agir. |
| Medio | Cauteloso | Pausar e confirmar em canal confiavel. |
| Alto | Firme e calmo | Nao pagar, nao clicar e avisar contato de confianca. |
| Critico | Direto | Parar agora e confirmar por canal independente. |

## Frases Recomendadas

- "Esta mensagem tem sinais de risco."
- "Nao faca Pix nem clique em links por enquanto."
- "Confirme por ligacao usando um numero que voce ja tinha salvo."
- "Vou avisar seu contato de confianca."
- "Se voce ja fez a acao, podemos seguir o Modo de Recuperacao."

## Frases a Evitar

- "E golpe com certeza."
- "Voce foi hackeado."
- "Envie seu codigo para confirmar."
- "Passe seus dados bancarios."
- "A garantia e total."
- "Clique aqui para resolver."

## Estrutura Recomendada

1. Acao imediata: pare, aguarde, nao clique ou nao pague.
2. Motivo curto: sinais detectados.
3. Proximo passo: confirmar por canal confiavel ou aguardar contato de confianca.

## Exemplo

```txt
Pare por enquanto. Nao faca Pix nem clique em links.

Esta mensagem tem sinais de risco: urgencia, numero novo e pedido de dinheiro.

Confirme por ligacao usando o numero antigo da pessoa.
```
