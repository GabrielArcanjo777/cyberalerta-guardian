# Como foi feito

## Declaração de uso de IA

Este projeto foi construído com uso intensivo de IA generativa (LLM) na implementação. Não é um detalhe escondido — é parte do método, e está escrito aqui para que ninguém descubra depois.

## Divisão real do trabalho

**Humano (eu):**
- defini o problema, o escopo e o que o sistema **não** pode fazer
- escolhi a arquitetura e rejeitei propostas
- rodei os testes, quebrei coisas, corrigi
- decidi o que ficava, o que saía e o que virava limitação documentada
- escrevi e revisei a documentação

**IA:**
- escreveu a maior parte do código
- propôs estrutura de módulos, nomes, testes e refatorações
- sugeriu correções a partir de falhas de teste

## O que isso significa se você for me entrevistar

Consigo explicar a arquitetura, o fluxo de uma mensagem até o alerta, e por que cada regra existe — inclusive as que eu decidi manter contra a sugestão da IA.

Não consigo recitar de memória cada linha de cada arquivo, e não vou fingir que consigo. Se a pergunta for "o que acontece na linha 214 de `hybrid/service.py`", a resposta honesta é "abre o arquivo comigo".

## O que está verificado

| Verificação | Como |
|---|---|
| Testes backend | `pytest app/tests -q`, local e no CI |
| Testes Android | `./gradlew testDevDebugUnitTest`, local |
| Typecheck frontend | `tsc --noEmit`, no CI |
| Lint frontend | `eslint . --max-warnings=0`, no CI |

## O que **não** está verificado

- nenhum teste com usuário real
- nenhuma auditoria de segurança externa
- nenhuma revisão de código por terceiros
- o dataset é sintético e gerado com IA — as métricas de precisão valem como regressão, não como desempenho
- o e2e do frontend não roda no CI (ver `demandas/001-melhorias-tecnicas`)

## Consequência

Trate como MVP de estudo. Não use em produção, não use para monitorar ninguém sem autorização explícita, e não confie nos números de acurácia como se fossem de campo.

## Por que manter público

Porque esconder o uso de IA não faz o código ficar melhor — só faz a pergunta aparecer na hora errada, na entrevista. Prefiro que ela apareça aqui.
