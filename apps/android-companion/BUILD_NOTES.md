# Android Companion — notas de build (Sprint 3, MVP)

Este projeto foi escrito **sem acesso a JDK, Gradle ou Android SDK** — a
máquina onde ele foi gerado não tem toolchain Android instalada. Nada aqui
foi compilado nem rodado. O código segue APIs estáveis e bem documentadas
(AndroidX Security, Keystore, Retrofit + kotlinx.serialization, Firebase
Messaging, Compose/Material3), mas o primeiro `Sync` no Android Studio deve
ser tratado como o verdadeiro primeiro compile — é esperado precisar de
pequenos ajustes (versões de dependência que o Android Studio sugerir
atualizar, algum import quebrado que passou despercebido).

## 1. Pré-requisitos

- Android Studio (Ladybug ou mais recente) com JDK 17 embutido.
- Android SDK Platform 35 + Build-Tools correspondentes (o próprio Android
  Studio resolve isso no primeiro Sync).
- Um projeto Firebase (gratuito) para o FCM — mesmo projeto cujas
  credenciais entram no backend (`FCM_PROJECT_ID`/`FCM_SERVICE_ACCOUNT_JSON`,
  ver `.env.example` na raiz do repo).

## 2. Gradle wrapper — passo manual obrigatório

**Não commitei `gradlew`, `gradlew.bat` nem `gradle/wrapper/gradle-wrapper.jar`.**
Escrever esses arquivos sem poder rodá-los depois arriscava entregar um
wrapper corrompido/desatualizado, o que é pior do que não ter nenhum. Ao
abrir `apps/android-companion` no Android Studio, ele detecta a ausência do
wrapper e oferece para gerar um automaticamente — aceite. Alternativa via
linha de comando, se tiver um Gradle instalado localmente:

```bash
cd apps/android-companion
gradle wrapper --gradle-version 8.7
```

## 3. Firebase / google-services.json

Os product flavors (`dev`, `staging`, `prod` — Secao 8.5 do Plano Mestre)
usam application ids diferentes (`com.cyberalerta.companion.dev`, `.staging`
e `com.cyberalerta.companion`). No Firebase Console, registre um app Android
para cada um que for usar e baixe o `google-services.json` correspondente
para:

```
app/src/dev/google-services.json       # flavor dev
app/src/staging/google-services.json   # flavor staging
app/src/main/google-services.json      # flavor prod (fallback default)
```

Para só validar o fluxo de pairing agora, basta o de `dev`. Sem o arquivo
certo no lugar certo, o plugin `com.google.gms.google-services` falha o
build com uma mensagem clara pedindo o arquivo — não é um bug se isso
acontecer no primeiro Sync.

`google-services.json` está no `.gitignore` (raiz do repo) — nunca commitar.

## 4. Rodando contra o backend local (flavor dev)

1. Suba o backend normalmente (`cd backend && uvicorn main:app --reload --port 8000`).
2. `dev` aponta para `http://10.0.2.2:8000/` — o alias do emulador Android
   para o localhost da máquina host. **Só funciona no emulador.** Em um
   aparelho físico na mesma rede, troque `API_BASE_URL` em
   `app/build.gradle.kts` (flavor `dev`) pelo IP da máquina rodando o
   backend, ou crie um flavor extra apontando pra ele.
3. `network_security_config.xml` libera cleartext HTTP só para
   `10.0.2.2`/`localhost` — staging/prod continuam HTTPS-only sem exceção.

## 5. Gerando um convite de pareamento pra testar

Ainda não existe UI de admin pronta (Console/Windows são Sprint 4) — o jeito
mais rápido de gerar um convite hoje é via API direta, com um usuário
`ADMIN`/`ANALYST` com `organization_id` setado e um `TRUSTED_CONTACT` na
mesma organização (veja `backend/app/tests/test_devices_pairing.py` para o
fixture exato de como esses usuários são criados nos testes — o mesmo
padrão serve pra criar um usuário real via `scripts/create_admin.py` +
ajuste manual do `organization_id`/papel `trusted_contact` no banco).

```
POST /devices/pairing-invitations
Authorization: sessão do ADMIN/ANALYST (cookie)
{ "trusted_contact_user_id": "<id do TRUSTED_CONTACT>" }
```

A resposta traz `token` (cole na tela de pareamento do app) e `expires_at`
(15 minutos por padrão).

## 6. Roteiro de validação manual (espelha o teste fim-a-fim do backend)

1. Gerar o convite (passo 5) → colar o token na tela de pareamento do app →
   "Parear".
2. Conferir no backend (`GET /devices/{id}`) que o device apareceu com
   `state=pending_pairing`.
3. Disparar `POST /devices/{id}/test-push` como admin.
4. O aparelho deve receber uma notificação do sistema.
5. Tocar na notificação → abre o app na tela do alerta → ACK "opened" é
   automático ao carregar.
6. Conferir que o device virou `state=active` (`GET /devices/{id}`).
7. `POST /devices/{id}/revoke` → qualquer ação seguinte no app (registrar
   token, abrir outro alerta) deve responder 401.

## 7. Lacunas conhecidas e decisões de escopo desta passada

Deixadas de fora deliberadamente — não são esquecimento, são o que o
backend atual (Sprint 2) consegue sustentar sem inventar dado que não existe:

- **Sem scanner de QR embutido.** Colar o token manualmente sempre funciona;
  um QR `cyberalerta://pair?token=...` escaneado por qualquer app de câmera/
  Google Lens já abre o app via deep link e pré-preenche o campo. Câmera
  in-app (CameraX + ML Kit) fica pra quando isso for uma reclamação real.
- **Sem lista de alertas/casos.** O backend só expõe buscar UM alerta por id
  (`GET /devices/me/alerts/{id}`) — não existe "listar todos os alertas
  deste device" ainda. Isso depende da integração real com Case (Sprint 5).
- **Sem botão "Ligar".** O payload do alerta nunca carrega telefone (Secao
  6.3 do plano — privacidade por padrão), e por enquanto só existe alerta
  TEST sintético, sem pessoa protegida real vinculada.
- **Sem classificação golpe/falso positivo/inconclusivo.** Mesma razão —
  precisa de um Case real por trás.
- **Chave de prova de posse gerada mas não desafiada.** `DeviceKeyProvider`
  gera o par de chaves no Keystore e manda a pública no pairing, mas o
  backend ainda não valida um desafio assinado contra ela (isso é hardening
  de Sprint 6, não bloqueador de Sprint 3).
- **ACK é best-effort, sem fila offline.** Se o ACK falhar por rede, ele não
  fica em fila local — reabrir o alerta tenta de novo. Fila offline
  criptografada (Secao 3.5 do plano) fica pra uma passada futura se isso
  virar problema real de uso.
- **Sem testes instrumentados/Compose UI test.** Só testes unitários puros
  em Kotlin (ViewModels + repositórios, via JUnit+MockK+kotlinx-coroutines-test,
  `app/src/test/`) — não precisam de emulador pra rodar
  (`./gradlew testDevDebugUnitTest`). Testes de UI instrumentados
  (`app/src/androidTest/`) ficam pra quando houver um emulador/dispositivo
  disponível pra rodar contra.

## 8. Assinatura e distribuição

Fora de escopo desta passada — o plano (Secao 8.5/10.1) trata isso como
"distribuição interna do APK/AAB" mais adiante, e assinatura de release só
importa perto de um piloto externo. `versionCode`/`versionName` estão
setados para um valor inicial (`1` / `0.1.0-sprint3`) só pra existir.
