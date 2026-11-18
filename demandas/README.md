# Demandas

Uma demanda é um pedido com contexto, critério de aceite e saída verificável. Tudo que não é bug urgente entra aqui antes de virar código.

## Estrutura de uma demanda

```text
demandas/
├── README.md
├── 001-melhoria-playwright-ci/
│   ├── especificacao.md
│   ├── analises/
│   └── entregas/
└── ...
```

## `especificacao.md` — o que precisa ter

1. **Problema** — o que está errado hoje, com evidência (arquivo, linha, saída de comando).
2. **Objetivo** — o que passa a ser verdade quando estiver pronto.
3. **Fora de escopo** — o que esta demanda não resolve.
4. **Critério de aceite** — como verificar, de forma executável.
5. **Risco** — o que pode quebrar.

## Regras

- Uma demanda = um problema. Se tem "e também", são duas.
- Sem critério de aceite executável, não é demanda: é ideia.
- Toda entrega registra o commit e o que foi verificado.

## Estados

`aberta` → `em andamento` → `entregue` · ou · `descartada` (com motivo)
