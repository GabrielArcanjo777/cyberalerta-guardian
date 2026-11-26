# 002 — E2E e Android verdes no CI

**Estado:** entregue · **Aberta em:** 2026-11-23 · **Origem:** demanda 001, itens 2 e 3 ("feito, ainda com `continue-on-error`")

Os jobs **E2E** e **Android** existiam no CI mas falhavam em todo push na `main`. Como estavam com `continue-on-error`, o CI aparecia verde mesmo assim.

| Pasta | Conteúdo |
|---|---|
| [`especificacao.md`](especificacao.md) | problema, objetivo, critério de aceite |
| [`fontes/`](fontes/) | trechos do log do CI que mostram as falhas |
| [`analises/`](analises/) | causa raiz de cada falha |
| [`entregaveis/`](entregaveis/) | o que mudou e como foi verificado |
