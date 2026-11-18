# Como foi feito

## Declaração

Este projeto foi desenvolvido com **agentes de IA**. Eu dirigi o processo: defini o problema, escolhi a arquitetura, delimitei o escopo e validei o resultado. Os agentes implementaram boa parte do código sob essa direção.

É um **projeto de estudo**. O objetivo é aprender engenharia de software na prática — arquitetura, testes, segurança, integração entre plataformas — e não lançar um produto.

## Como o trabalho foi dividido

**Eu:**
- defini o problema, o escopo e as regras que o sistema não pode violar
- escolhi a arquitetura e rejeitei abordagens propostas
- rodei os testes, encontrei as falhas e pedi correção
- decidi o que ficava, o que saía e o que virava limitação documentada
- revisei toda a documentação

**Agentes:**
- implementaram módulos, testes e refatorações
- propuseram estrutura de pastas, nomes e alternativas de solução

## O que isso me deu

- prática de arquitetura num sistema com quatro componentes: API, painel web, app Android e app desktop
- prática de revisão técnica: ler o que um agente escreveu e decidir se presta, se quebra algo, se dá para manter
- prática de teste e CI: suíte de backend, suíte de Android, typecheck e lint no frontend

Dirigir agentes é uma habilidade real de engenharia. Quem só sabe escrever código na mão não consegue fazer isso — e quem só sabe pedir para a IA não consegue manter.

## O que está verificado

| Verificação | Como |
|---|---|
| Testes backend | `pytest app/tests -q`, local e no CI |
| Testes Android | `./gradlew testDevDebugUnitTest`, local |
| Typecheck frontend | `tsc --noEmit`, no CI |
| Lint frontend | `eslint . --max-warnings=0`, no CI |

## O que ainda não está verificado

- nenhum teste com usuário real
- nenhuma auditoria de segurança externa
- o dataset é sintético e gerado com IA — as métricas valem como regressão, não como desempenho
- o e2e do frontend não roda no CI (ver `demandas/001-melhorias-tecnicas`)

## Conclusão

Projeto de estudo, código aberto, com limites declarados. Serve para mostrar o que eu consigo construir e manter com apoio de agentes — e para aprender o que ainda não sei.
