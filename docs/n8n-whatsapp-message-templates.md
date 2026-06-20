# Templates WhatsApp/n8n

Templates curtos para uso em WhatsApp via n8n. O n8n orquestra o envio; o CyberAlerta Guardian decide risco, sinais e proximo passo.

## Variaveis

| Variavel | Descricao |
| --- | --- |
| `{{protected_person_name}}` | Nome ou apelido da pessoa protegida. |
| `{{trusted_contact_name}}` | Contato de confianca. |
| `{{risk_level}}` | Baixo, medio, alto ou critico. |
| `{{signals}}` | Lista curta de sinais detectados. |
| `{{case_id}}` | Identificador do caso. |
| `{{next_best_action}}` | Proximo passo recomendado pelo backend. |

## Pessoa Protegida

### Risco baixo

```txt
Recebi sua mensagem. Nao vi sinais fortes de golpe, mas vale confirmar antes de agir.

Se houver pedido de dinheiro, codigo ou link, confira por um canal confiavel.
```

### Risco medio

```txt
Pausa por enquanto. Esta mensagem tem alguns sinais de risco.

Nao clique em links nem envie codigo antes de confirmar por outro canal.
```

### Risco alto

```txt
Nao faca Pix nem clique em links por enquanto.

Esta mensagem tem sinais de risco: {{signals}}.

Vou avisar seu contato de confianca.
```

### Risco critico

```txt
Pare agora. Nao faca Pix, nao clique em links e nao envie codigos.

Detectamos sinais fortes de golpe: {{signals}}.

Confirme por ligacao usando um numero que voce ja tinha salvo.
```

## Contato de Confianca

```txt
Alerta CyberAlerta Guardian

{{protected_person_name}} recebeu uma mensagem com sinais de risco.
Risco: {{risk_level}}.
Sinais: {{signals}}.

Ligue para a pessoa usando um numero conhecido antes de qualquer pagamento ou clique.
Caso: {{case_id}}.
```

## Recovery

```txt
Modo de Recuperacao iniciado.

1. Fale com seu banco ou instituicao agora.
2. Guarde comprovantes e a conversa.
3. Nao envie mais dinheiro.
4. Troque senhas se enviou codigo, senha ou instalou app.
5. Registre ocorrencia com as evidencias.
```

## Erro Seguro

```txt
Nao consegui concluir a analise agora.

Por seguranca, nao faca pagamento, nao clique em links e nao envie codigos ate confirmar por um canal confiavel.
```

## Payload Sugerido para n8n

```json
{
  "to": "{{whatsapp_destination}}",
  "body": "{{whatsapp_user_message}}",
  "case_id": "{{case_id}}",
  "dry_run": true
}
```

## Regras de Uso

- Use `DRY_RUN=true` em demo e desenvolvimento.
- Nao envie telefone completo para logs.
- Nao salve mensagem completa por padrao.
- Nao prometa protecao garantida.
- Nunca peca senha, token, codigo ou dado bancario pelo WhatsApp.
