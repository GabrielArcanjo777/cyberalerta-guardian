# Windows Shell (Tauri) — notas de build (Sprint 4, MVP)

**Como isso foi validado:** a máquina não tinha Rust nem Visual Studio Build
Tools instalados. Instalei os dois (`rustup` via winget + VS Build Tools
17.14 com o workload C++), montei o projeto do zero e rodei o build/execução
real (`cargo build`, `cargo run`) várias vezes até compilar limpo — não é
código escrito às cegas. Como o ambiente que fez essa validação não tem uma
sessão de desktop interativa de verdade, a janela abria minimizada
(coordenadas -32000,-32000, estado padrão do Windows) e capturas de tela do
"desktop" mostravam outra coisa. Não dava pra confirmar visualmente clicando
com mouse. Em vez de assumir que funcionava, subi o app com
`WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS=--remote-debugging-port=9222` e
dirigi a sessão real via Chrome DevTools Protocol (WebSocket bruto, sem
Playwright — não existe driver Tauri/WebView2 pronto): naveguei pra
`/login.html`, preenchi o formulário de verdade (`admin@cyberalerta.local`),
disparei o submit real e confirmei a navegação pra `/mfa` — ou seja, login
end-to-end contra o backend real, não um mock. **Ainda assim, ninguém
confirmou visualmente a janela num monitor de verdade — isso fica pendente
pra você na primeira vez que rodar localmente.**

## 1. Decisão de arquitetura: build estático embutido, não URL remota

O Plano Mestre (Secao 3.4) permite "build estático ou roteamento
compatível". Escolhi **build estático** (`next build` com
`output:'export'`, ativado só quando `BUILD_TARGET=tauri`) em vez de
apontar o webview pra URL do Web hospedado, porque:

- O frontend já é 100% client-side fetch contra `NEXT_PUBLIC_API_URL`
  (`lib/api.ts`), sem middleware nem API routes do Next — nenhum rework de
  rota/auth foi necessário pra exportar estático. Validado com
  `next build` real antes de mexer em qualquer linha de Rust.
- Zero duplicação de lógica: Console/Admin/MFA são o mesmo React do Web.

**Problema real que isso cria e como foi resolvido:** dentro do webview
Tauri a origem é `http://tauri.localhost`, diferente da API cloud — um
`fetch()` de navegador não manda o cookie de sessão (`SameSite=Lax`,
cross-site) e a CSP bloquearia a chamada de qualquner forma. Resolvido com
`@tauri-apps/plugin-http`: o fetch roda no lado Rust (`reqwest`), fora do
contexto de navegador — sem CORS, sem SameSite, sem CSP `connect-src` — e
mantém seu próprio cookie jar. **Zero mudança no backend foi necessária**
(nem CORS, nem cookie `SameSite`) porque CORS é uma politica só de
navegador; um cliente HTTP não-browser simplesmente ignora esses headers.
Todo `fetch()` de `lib/api.ts` foi trocado por `apiFetch()`
(`lib/platformFetch.ts`), que escolhe entre o fetch nativo (Web) e o do
plugin (Tauri) em runtime.

## 2. Só o Console vai no instalador — não o site inteiro

**Correção de escopo pedida durante a sessão:** a primeira versão exportava
literalmente todas as 20 rotas do Next (landing page, `/before-pix`,
`/chatbot-demo`, `/simulator`, `/ml-lab`, `/trust-center`, `/pilot`, etc.) —
uma cópia inteira do site de marketing dentro do `.exe`. Isso está errado:
o Plano Mestre (Secao 3.4) descreve o app Windows como casca de
autenticação + Console/Admin, não o site público.

Fix: `frontend/scripts/prune-tauri-export.mjs` roda depois de
`next build` (só quando `BUILD_TARGET=tauri`, via `npm run build:tauri`) e
apaga do `out/` estático tudo que não for `login`, `mfa`, `admin`,
`family-console` ou `whatsapp-setup` (+ `_next/`, `404.html`, `icon.svg`).
Resultado: `out/` caiu de 4,7MB/20 rotas pra 2,3MB/5 rotas. A janela abre
direto em `login.html` (`tauri.conf.json` → `app.windows[0].url`), não na
landing page.

Como o `Header.tsx` (marca + nav de marketing) é compartilhado entre as
páginas de Console e a landing page, ele agora checa `isTauriRuntime()`
(`lib/runtime.ts`) pra esconder a nav de marketing e trocar o link da marca
pro Console em vez de `/` (que não existe mais no bundle). Dois links
mortos achados e corrigidos em `GuardianAdminConsole.tsx` (`/trust-center`,
`/chatbot-demo` — só apareciam escondidos num accordion, escondidos agora
também quando `isTauri`).

**Contrapartida no site (Web):** como o instalador não existe pra baixar
ainda (ver seção 4), o `Header.tsx` do Web ganhou um link "Baixar para
Windows" apontando pro `Releases` do repo público no GitHub — funciona de
verdade assim que a primeira release for publicada lá, sem inventar URL.

## 3. Tray, deep links, CSP

- **Tray** (`src/lib.rs`): status (não-clicável), abrir Console, desconectar
  (emite evento `tray://disconnect-requested` — o frontend escuta em
  `TauriDeepLinkBridge.tsx`, chama `postLogout()` de verdade e navega pra
  `/login`), sair. Fechar a janela minimiza pra tray em vez de matar o
  processo (`CloseRequested` → `hide()` + `prevent_close()`).
- **Deep links**: `cyberalerta://` registrado via `tauri-plugin-deep-link`.
  `cyberalerta://case/{id}` ainda não tem rota de detalhe de caso no
  Console Web (isso é Sprint 5 — integração real com `Case`) — por enquanto
  leva pro `/admin`, documentado como limitação temporária no código
  (`TauriDeepLinkBridge.tsx`). `cyberalerta://pair` não se aplica ao
  Windows (só Android pareia) e é só logado.
- **CSP** (`tauri.conf.json` → `app.security.csp`): `script-src 'self'
  'unsafe-inline'` (o app tem um script inline pequeno de anti-flash de
  tema, sem conteúdo de usuário), `style-src`/`font-src` liberando
  `fonts.googleapis.com`/`fonts.gstatic.com` (achado rodando de verdade —
  sem isso a fonte Inter não carregava). Nenhum domínio da API precisa estar
  em `connect-src`, porque o plugin HTTP não passa pela CSP do webview.
- **Capabilities** (`src-tauri/capabilities/default.json`): só
  `http:default` (escopado pra `localhost:8000`/`127.0.0.1:8000` — **trocar
  pra URL real de staging/prod antes de buildar pra esses ambientes**),
  `deep-link:default`, `store:default` e um punhado de permissões de janela.

## 4. Assinatura de código — BLOQUEADO, ação sua, não posso fazer isso

O Plano Mestre (Secao 10.1/10.2, risco "Assinatura/publicação — NOVO")
já marcava isso como item de lead-time longo a iniciar desde o Sprint 0 —
não encontrei nenhuma evidência no repo de que isso tenha sido feito.
**Não tentei e não vou tentar comprar/adquirir um certificado** — isso
envolve verificação de identidade/empresa junto a uma CA e dados de
pagamento, uma decisão e ação seu, não algo que um agente deveria fazer
sozinho. `tauri.conf.json` não tem `bundle.windows.certificateThumbprint`
de propósito — o instalador gerado hoje é **não-assinado**, e o
SmartScreen vai avisar o usuário no primeiro uso. Mesmo padrão do Android
(APK de debug, "internal testing"): funcional pra validar, não pronto pra
distribuir pro público-alvo (idosos, exatamente quem mais estranha o aviso
do SmartScreen).

## 5. Rodando localmente

Pré-requisitos (nenhum existia nesta máquina antes desta sessão):

```powershell
winget install --id Rustlang.Rustup -e
winget install --id Microsoft.VisualStudio.2022.BuildTools -e --override "--quiet --wait --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
```

WebView2 Runtime já vem pré-instalado no Windows 10/11 atualizado — não
precisou instalar nada extra pra isso.

```bash
cd apps/windows-shell
npm install
$env:NEXT_PUBLIC_API_URL = "http://127.0.0.1:8000"   # ou a URL real de staging/prod
npx tauri dev     # ou: npx tauri build (gera o instalador NSIS não-assinado)
```

`beforeDevCommand`/`beforeBuildCommand` já chamam
`frontend/package.json`'s `build:tauri` (export estático + poda) — não
precisa rodar isso manualmente antes.

## 6. Lacunas conhecidas (decisões de escopo desta passada, não esquecimento)

- **Sessão não persiste entre reinícios do app.** O cookie jar do
  `tauri-plugin-http` é em memória (nada na documentação oficial menciona
  persistência em disco) — fechar e abrir o app de novo exige logar de
  novo. Isso não bloqueia o critério de aceite da Sprint 4 (que não fala de
  persistência), mas diverge de "token salvo no cofre seguro do sistema"
  (Secao 3.4) — ficaria pra uma passada de hardening, talvez com Stronghold
  ou serializando os cookies via `tauri-plugin-store` no diretório de dados
  do app.
- **Requests de prefetch RSC do Next 16 retornam 500** contra o servidor de
  assets estático simples do Tauri (`__next.<rota>.__PAGE__.txt?_rsc=...`)
  — parece um descompasso entre o nome de arquivo que o export estático
  gera e o que o roteador cliente do Next 16 pede pra prefetch quando
  servido por um asset server que não é Next/Vercel. **Não bloqueia nada**
  (a navegação real cai pra reload completo e funciona, confirmado ao vivo
  via CDP), só gera ruído no console/rede. Não persegui a causa raiz essa
  noite.
- **`cyberalerta://case/{id}` não abre o caso específico** — vai pro
  `/admin` genérico. Precisa de uma rota de detalhe de caso no Console Web
  que ainda não existe (nem pro Web nem pro Windows) — isso é Sprint 5.
- **Sem updater configurado.** `tauri.conf.json` não tem plugin de
  atualização — "Updater assinado, canal stable e rollback documentado"
  (Secao 3.4) fica pra quando tiver um canal de distribuição real pra
  atualizar contra.
- **Tray/deep link não testados clicando de verdade** (só via CDP —
  `Runtime.evaluate`/`Page.navigate`, que não simula o menu nativo do
  tray). A lógica em `src/lib.rs` compila e os handlers foram revisados,
  mas ninguém apertou "Desconectar" no menu de bandeja de verdade ainda.
