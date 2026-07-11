# -*- coding: utf-8 -*-
"""Dataset rotulado v1 — mensagens sintéticas em PT-BR para avaliação do detector.

Provenance: escrito à mão (sintético), inspirado em padrões públicos e amplamente
documentados de golpes por WhatsApp no Brasil. NÃO contém mensagens reais nem
dados pessoais reais. Cada entrada é distinta (sem augmentation automática —
trocar nomes/valores não altera os sinais das regras, então inflaria o N sem
adicionar informação).

Labels:
  - "scam": mensagem de golpe (com scam_type da taxonomia do projeto)
  - "legit": mensagem legítima (com category para análise de falsos positivos)

Os "hard negatives" são intencionais: mensagens legítimas que citam pix, senha,
código, banco, urgência e links — exatamente onde regras por palavra-chave erram.
"""

# (scam_type, text)
SCAM: list[tuple[str, str]] = [
    # --- FAMILY_IMPERSONATION: parente falso + número novo + pix (25)
    ("FAMILY_IMPERSONATION", "Oi mae, troquei de numero. Preciso que voce faca um pix urgente pra mim, depois te explico."),
    ("FAMILY_IMPERSONATION", "Mae sou eu, quebrei meu celular e to com esse numero novo. Consegue me emprestar 800 reais no pix agora?"),
    ("FAMILY_IMPERSONATION", "Pai, e o Lucas. Meu chip queimou, esse e meu numero novo. Preciso pagar um boleto hoje, me ajuda com um pix?"),
    ("FAMILY_IMPERSONATION", "Vo, sou seu neto. Estou com um problema serio e preciso de dinheiro agora. Nao liga pro meu numero antigo que foi clonado."),
    ("FAMILY_IMPERSONATION", "Amor, troquei de numero, salva esse. Preciso muito de um favor, faz um pix de 350 pra essa chave, te devolvo amanha."),
    ("FAMILY_IMPERSONATION", "Tia, meu telefone molhou, to usando esse provisorio. A senhora consegue fazer uma transferencia pra mim hoje ainda?"),
    ("FAMILY_IMPERSONATION", "Mae, nao conta pro pai, mas preciso de 500 reais urgente. Faz o pix nessa chave que te mando agora."),
    ("FAMILY_IMPERSONATION", "Oi, e o filho da Dona Marta? Sou seu primo, numero novo. Preciso quitar uma divida agora, me faz um pix que semana que vem devolvo."),
    ("FAMILY_IMPERSONATION", "Oi pai, celular novo. O antigo foi roubado, nao liga la. Preciso que pague um boleto pra mim agora, e urgente."),
    ("FAMILY_IMPERSONATION", "Mae, e a Julia. Esse e meu numero novo. To no hospital e preciso pagar o exame agora, faz um pix de 620?"),
    ("FAMILY_IMPERSONATION", "Filha, e o papai. Perdi o celular e to no numero de um amigo. Me manda um pix de 300 que depois te explico tudo."),
    ("FAMILY_IMPERSONATION", "Oi vo, mudei de numero. Nao fala com ninguem sobre isso, mas to devendo uma pessoa perigosa e preciso de dinheiro agora."),
    ("FAMILY_IMPERSONATION", "Mana, meu celular pifou. Me empresta 450 no pix ate sexta? E urgente, confia em mim."),
    ("FAMILY_IMPERSONATION", "Oi mae, to escrevendo do numero da minha colega. Preciso que transfira 900 agora pra nao perder a matricula."),
    ("FAMILY_IMPERSONATION", "Pai, troquei de chip. Faz um favor: paga esse boleto de 780 hoje que amanha te devolvo, nao liga que to em reuniao."),
    ("FAMILY_IMPERSONATION", "Oi tio, e seu sobrinho. Novo numero. Surgiu uma emergencia e preciso muito de 250 no pix agora."),
    ("FAMILY_IMPERSONATION", "Mae, sou eu. Emprestaram esse celular pra mim. Caiu minha venda e preciso pagar o fornecedor agora, pix de 1200, por favor."),
    ("FAMILY_IMPERSONATION", "Vozinha, e o Pedrinho. Troquei de numero. Nao conta pra mamae, mas preciso de uma grana urgente hoje."),
    ("FAMILY_IMPERSONATION", "Amor, esse e meu numero temporario. Me faz um pix de 200 agora que meu cartao bloqueou e to sem almoco."),
    ("FAMILY_IMPERSONATION", "Oi pai, e a Bia do numero novo. Bateram no meu carro e preciso pagar o guincho agora. Me manda 600 por pix?"),
    ("FAMILY_IMPERSONATION", "Mae, meu whats antigo foi hackeado, usa so esse. Preciso que faca uma transferencia agora, depois acerto contigo."),
    ("FAMILY_IMPERSONATION", "E o Joao, primo da Renata. To com numero novo. Consegue me adiantar 350 no pix hoje? E emergencia de verdade."),
    ("FAMILY_IMPERSONATION", "Oi mae, celular na assistencia, to com esse aqui. Paga um boleto pra mim agora? Vence hoje e nao consigo pelo app."),
    ("FAMILY_IMPERSONATION", "Pai, nao liga nesse numero que so pega mensagem. Preciso urgente de 400 pra resolver um problema no banco."),
    ("FAMILY_IMPERSONATION", "Filho, aqui e a mamae com numero novo. Me manda o codigo que chegou no seu celular pra eu recuperar minha conta, rapido."),

    # --- BANK_IMPERSONATION: falso banco / central de segurança (20)
    ("BANK_IMPERSONATION", "Central de seguranca do seu banco: detectamos uma compra suspeita de 2.450,00. Para cancelar, confirme o codigo enviado por SMS."),
    ("BANK_IMPERSONATION", "Banco informa: seu cartao foi clonado. Ligue imediatamente ou confirme seus dados aqui para bloqueio preventivo."),
    ("BANK_IMPERSONATION", "Prezado cliente, sua conta sera bloqueada em 24h. Regularize agora pelo link https://atualiza-conta-segura.top"),
    ("BANK_IMPERSONATION", "Aqui e do departamento de fraudes. Identificamos um pix nao reconhecido. Me informe o token do seu aplicativo para estorno."),
    ("BANK_IMPERSONATION", "Seu acesso foi suspenso por atividade incomum. Envie sua senha de 6 digitos para validacao imediata."),
    ("BANK_IMPERSONATION", "Atencao: emprestimo de 8.000 aprovado em seu CPF. Caso nao reconheca, confirme o codigo SMS agora para cancelar."),
    ("BANK_IMPERSONATION", "Banco: atualizacao cadastral obrigatoria ate hoje. Acesse www.cadastro-bancoseguro.net e informe seus dados."),
    ("BANK_IMPERSONATION", "Sou o gerente da sua agencia. Houve uma tentativa de invasao. Preciso que me passe o codigo do seu token agora."),
    ("BANK_IMPERSONATION", "Compra de R$ 1.899 em MERCADOLIVRE aprovada. Nao foi voce? Clique no link para contestar: http://contesta-compra.info"),
    ("BANK_IMPERSONATION", "Sua chave pix sera desativada hoje. Para manter, confirme a senha do aplicativo neste atendimento."),
    ("BANK_IMPERSONATION", "Central 24h: bloqueio preventivo ativado. Digite os 4 ultimos digitos do cartao e a senha para desbloquear agora."),
    ("BANK_IMPERSONATION", "Detectamos acesso ao seu internet banking em outro estado. Se nao foi voce, me informe o codigo de verificacao recebido."),
    ("BANK_IMPERSONATION", "Seu limite foi reduzido por seguranca. Para restaurar agora, valide seus dados no link https://valida-limite.site"),
    ("BANK_IMPERSONATION", "Cliente, ha um pagamento agendado suspeito de 3.200. Responda com o token do app em ate 10 minutos para cancelar."),
    ("BANK_IMPERSONATION", "Banco Central comunica: seu CPF consta com pendencia grave. Evite bloqueio pagando a taxa de regularizacao hoje."),
    ("BANK_IMPERSONATION", "Seguranca digital: instale o modulo de protecao pelo link para evitar novo golpe no seu cartao: www.modulo-protecao.org"),
    ("BANK_IMPERSONATION", "Sua fatura tem cobranca duplicada. Para estorno imediato, informe numero do cartao e codigo de seguranca."),
    ("BANK_IMPERSONATION", "Aviso urgente: pix de 1.750 em processamento. Cancele agora respondendo com a senha do aplicativo."),
    ("BANK_IMPERSONATION", "Atendimento prioritario: seu cadastro expira hoje. Confirme agencia, conta e senha para nao perder o acesso."),
    ("BANK_IMPERSONATION", "Ola, falo do setor antifraude. Vamos estornar uma cobranca indevida, mas preciso que confirme o codigo que acabou de chegar."),

    # --- CREDENTIAL_THEFT: roubo de código do WhatsApp / senhas (10)
    ("CREDENTIAL_THEFT", "Oi! Te mandei um codigo de 6 digitos por engano, pode me passar? E rapidinho, desculpa o incomodo."),
    ("CREDENTIAL_THEFT", "Aqui e do suporte do WhatsApp. Sua conta sera desativada. Envie o codigo de verificacao recebido para manter o acesso."),
    ("CREDENTIAL_THEFT", "Amiga, caiu um codigo ai no seu celular? Era pra mim, me manda por favor que preciso agora."),
    ("CREDENTIAL_THEFT", "Estamos validando seu numero para o sorteio. Informe o codigo SMS que acabou de receber para confirmar participacao."),
    ("CREDENTIAL_THEFT", "Seu WhatsApp sera duplicado por seguranca. Digite aqui o token de 6 digitos que enviamos agora."),
    ("CREDENTIAL_THEFT", "Oi, sou eu da loja. Pra liberar seu cupom preciso do codigo que chegou no seu SMS, me passa rapidinho?"),
    ("CREDENTIAL_THEFT", "Equipe tecnica: detectamos tentativa de clonagem. Confirme sua senha atual para ativarmos a protecao."),
    ("CREDENTIAL_THEFT", "Voce foi selecionado para verificacao de conta. Responda com o codigo recebido agora ou perdera o numero."),
    ("CREDENTIAL_THEFT", "Mano, fiz besteira e coloquei seu numero no meu cadastro. Chegou um codigo ai? Me manda que corrijo aqui."),
    ("CREDENTIAL_THEFT", "Suporte: para concluir a portabilidade do seu chip, informe o token enviado por SMS imediatamente."),

    # --- MALICIOUS_LINK: link + urgência/cadastro (15)
    ("MALICIOUS_LINK", "Urgente: clique neste link https://regularizacao-conta.top para atualizar seu cadastro e evitar bloqueio hoje."),
    ("MALICIOUS_LINK", "Seu CPF foi sorteado! Acesse agora www.premio-liberado.click e resgate antes que expire."),
    ("MALICIOUS_LINK", "Detectamos virus no seu aparelho. Instale a limpeza urgente por aqui: http://limpa-celular.app"),
    ("MALICIOUS_LINK", "Sua declaracao caiu na malha fina. Regularize hoje pelo link oficial: https://receita-regulariza.net"),
    ("MALICIOUS_LINK", "Promocao relampago so hoje: iPhone por 899. Garanta agora no link www.ofertas-imperdiveis.buzz"),
    ("MALICIOUS_LINK", "Seu pacote esta retido. Pague a taxa de liberacao agora em https://rastreio-entrega.info ou sera devolvido."),
    ("MALICIOUS_LINK", "Atualizacao obrigatoria do aplicativo do banco. Baixe imediatamente aqui: http://app-banco-novo.xyz"),
    ("MALICIOUS_LINK", "Voce tem valores a receber do governo. Consulte agora com CPF e senha em www.valores-esquecidos.top"),
    ("MALICIOUS_LINK", "Fotos suas estao circulando nesse site, olha aqui antes que apaguem: http://veja-agora.click"),
    ("MALICIOUS_LINK", "Seu plano de saude sera cancelado hoje. Evite a perda atualizando seus dados no link https://plano-atualiza.site"),
    ("MALICIOUS_LINK", "ULTIMO AVISO: fatura em atraso. Pague agora pelo link para evitar negativacao: www.pagamento-rapido.cc"),
    ("MALICIOUS_LINK", "Recadastramento do auxilio termina hoje. Nao perca o beneficio: https://auxilio-recadastro.org"),
    ("MALICIOUS_LINK", "Seu email sera excluido em 2 horas. Mantenha a conta confirmando a senha aqui: http://mantenha-email.net"),
    ("MALICIOUS_LINK", "Vaga urgente confirmada. Complete a contratacao enviando seus documentos neste link: www.rh-contrata.click"),
    ("MALICIOUS_LINK", "Multa pendente no seu CPF. Consulte e pague com desconto de 40% so hoje: https://multa-desconto.info"),

    # --- FAKE_INVOICE_OR_BOLETO (10)
    ("FAKE_INVOICE_OR_BOLETO", "Segue segunda via do boleto do condominio com vencimento hoje. Pague ate as 18h para evitar multa."),
    ("FAKE_INVOICE_OR_BOLETO", "Sua fatura do cartao fechou com desconto de 35% para pagamento a vista hoje via boleto. Aproveite agora."),
    ("FAKE_INVOICE_OR_BOLETO", "Financeiro: identificamos boleto em aberto no seu CPF. Regularize agora para nao protestar em cartorio."),
    ("FAKE_INVOICE_OR_BOLETO", "Atualizamos o boleto da sua mensalidade, o anterior perdeu a validade. Pague por este novo codigo hoje."),
    ("FAKE_INVOICE_OR_BOLETO", "Cobranca: parcela do seu emprestimo vence hoje. Evite juros pagando agora pelo boleto atualizado que segue."),
    ("FAKE_INVOICE_OR_BOLETO", "Seu seguro sera cancelado por falta de pagamento. Segue boleto com valor promocional valido so ate hoje."),
    ("FAKE_INVOICE_OR_BOLETO", "Prezado, a nota do seu pedido gerou imposto pendente. Pague o boleto anexo agora para liberar a entrega."),
    ("FAKE_INVOICE_OR_BOLETO", "Departamento de cobranca: acordo com 60% de desconto valido ate as 17h de hoje. Boleto segue abaixo, pague agora."),
    ("FAKE_INVOICE_OR_BOLETO", "Reemissao automatica: seu boleto do plano foi atualizado com novo codigo de barras. Quite hoje para manter o servico."),
    ("FAKE_INVOICE_OR_BOLETO", "Ultima chance de renegociar sua divida com desconto. Boleto expira hoje as 20h, efetue o pagamento imediatamente."),

    # --- DELIVERY_SCAM (10)
    ("DELIVERY_SCAM", "Correios: sua encomenda esta retida na alfandega. Pague a taxa de 12,90 agora para liberar a entrega."),
    ("DELIVERY_SCAM", "Transportadora: tentamos entregar seu pacote 2 vezes. Agende nova entrega pagando a taxa pelo link agora."),
    ("DELIVERY_SCAM", "Seu pedido internacional foi taxado. Efetue o pagamento hoje ou o item sera devolvido ao remetente."),
    ("DELIVERY_SCAM", "Ola, sou o entregador. Seu endereco nao foi localizado. Pague a taxa de reentrega agora por pix para eu voltar."),
    ("DELIVERY_SCAM", "Encomenda bloqueada por divergencia cadastral. Atualize os dados e pague a tarifa de liberacao imediatamente."),
    ("DELIVERY_SCAM", "SEDEX parado no centro de distribuicao. Liberacao mediante taxa de armazenagem, pague hoje para nao perder o prazo."),
    ("DELIVERY_SCAM", "Seu iPhone comprado no sorteio chegou! So falta pagar o frete de 29,90 via pix agora para agendar a entrega."),
    ("DELIVERY_SCAM", "Alfandega: tributo pendente sobre sua importacao. Pagamento imediato evita multa diaria e devolucao."),
    ("DELIVERY_SCAM", "Motoboy a caminho, mas o sistema exige confirmacao da taxa de seguro. Faz o pix de 15 agora pra ele nao retornar."),
    ("DELIVERY_SCAM", "Sua entrega premium foi priorizada. Confirme o pagamento da diferenca de frete agora pelo link para receber hoje."),

    # --- PRIZE_OR_LOTTERY (10)
    ("PRIZE_OR_LOTTERY", "PARABENS! Voce ganhou 5.000 reais no sorteio da loja. Pague apenas a taxa de liberacao de 47 para receber hoje."),
    ("PRIZE_OR_LOTTERY", "Seu numero foi premiado no sorteio do aniversario da rede. Resgate agora informando seus dados e pagando o frete do premio."),
    ("PRIZE_OR_LOTTERY", "Voce foi contemplado com um vale-compras de 1.000. Confirme com pix de validacao de 25 em ate 1 hora."),
    ("PRIZE_OR_LOTTERY", "Sorteio oficial: sua conta ganhou um carro 0km! Para iniciar a transferencia, quite o imposto do premio hoje."),
    ("PRIZE_OR_LOTTERY", "Ganhou! Cupom premiado detectado no seu CPF. Ligue agora ou pague a taxa administrativa para nao perder."),
    ("PRIZE_OR_LOTTERY", "Promocao dos 30 anos: voce levou uma TV 55. Basta pagar o seguro de envio de 39,90 agora por pix."),
    ("PRIZE_OR_LOTTERY", "Ultima etapa do sorteio: deposite a caucao reembolsavel de 60 hoje e receba seu premio de 8.000 amanha."),
    ("PRIZE_OR_LOTTERY", "Voce e o vencedor da semana! Confirme identidade enviando documento e taxa de cadastro em ate 2 horas."),
    ("PRIZE_OR_LOTTERY", "Seu telefone foi sorteado com bonus em dinheiro. Ative o resgate agora com um pix simbolico de 19,99."),
    ("PRIZE_OR_LOTTERY", "Notificacao de premio acumulado no seu nome. Liberacao imediata mediante pagamento da tarifa cartorial hoje."),

    # --- FAKE_JOB (10)
    ("FAKE_JOB", "Vaga home office pagando 350 por dia! Comece hoje mesmo, basta pagar o kit de cadastro de 49,90."),
    ("FAKE_JOB", "RH selecionou seu curriculo. Para garantir a vaga, efetue o pagamento do exame admissional agora pelo link."),
    ("FAKE_JOB", "Trabalhe curtindo videos e ganhe 200 por dia. Deposito inicial de 35 para ativar sua conta de tarefas."),
    ("FAKE_JOB", "Emprego confirmado! Envie 60 reais da taxa do crachá e uniforme hoje para iniciar amanha."),
    ("FAKE_JOB", "Renda extra garantida: revenda nossos produtos. Compre o kit inicial com desconto so hoje e comece a lucrar."),
    ("FAKE_JOB", "Sua entrevista foi aprovada. Ultima etapa: pagamento do curso obrigatorio de integracao, vagas limitadas hoje."),
    ("FAKE_JOB", "Empresa internacional contrata digitadores. Cadastro urgente mediante taxa unica, retorno em dobro na primeira semana."),
    ("FAKE_JOB", "Parabens, voce foi selecionado! Confirme a vaga com pix de 45 para o material de treinamento agora."),
    ("FAKE_JOB", "Ganhe avaliando aplicativos no celular. Ative seu perfil pagando a mensalidade promocional hoje mesmo."),
    ("FAKE_JOB", "Vaga urgente de motorista. Garanta ja: taxa de analise de documentos de 30 reais via pix agora."),

    # --- INVESTMENT_SCAM (10)
    ("INVESTMENT_SCAM", "Investimento com retorno garantido de 20% ao mes. Comece com 100 hoje e resgate quando quiser, sem risco."),
    ("INVESTMENT_SCAM", "Grupo VIP de trader milionario liberado por 24h. Deposite 250 agora e receba os sinais que nunca erram."),
    ("INVESTMENT_SCAM", "Multiplique seu dinheiro: aporte de 500 vira 1.500 em 7 dias. Plataforma com saque garantido, entre hoje."),
    ("INVESTMENT_SCAM", "Robo de investimentos com 98% de acerto. Ultimas vagas do plano promocional, ative agora com pix."),
    ("INVESTMENT_SCAM", "Cripto exclusiva antes do lancamento: compre hoje a 0,10 e venda a 1,00 na proxima semana. Lucro certo."),
    ("INVESTMENT_SCAM", "Consultor autorizado: dobre sua aposentadoria em 60 dias com nosso fundo privado. Deposito minimo hoje de 300."),
    ("INVESTMENT_SCAM", "Renda passiva garantida: alugue seu limite do cartao e receba 15% ao mes. Sem burocracia, comece agora."),
    ("INVESTMENT_SCAM", "Oportunidade unica: acoes da empresa antes da bolsa. Retorno minimo assegurado em contrato, invista hoje."),
    ("INVESTMENT_SCAM", "Mesa proprietaria paga ate 40% ao mes. Taxa de adesao promocional so hoje, garanta sua vaga com pix."),
    ("INVESTMENT_SCAM", "Seu vizinho ja esta lucrando 3.000 por semana no nosso app. Deposite 150 e comece em 5 minutos, garantido."),

    # --- EXTORTION (8)
    ("EXTORTION", "Tenho fotos intimas suas e da sua familia. Pague 2.000 em pix ate hoje a noite ou publico tudo nas redes."),
    ("EXTORTION", "Invadi seu computador e gravei sua camera. Deposite 1.500 em criptomoeda em 48h ou envio o video aos seus contatos."),
    ("EXTORTION", "Sei onde sua filha estuda. Se nao quiser problema, transfira 3.000 hoje e nao procure a policia."),
    ("EXTORTION", "Seu marido tem uma divida conosco. Pague 5.000 ate amanha ou vamos atras da sua familia. Nao conte a ninguem."),
    ("EXTORTION", "Hackeamos seus emails e temos suas conversas. Ultima chance: pix de 800 agora ou tudo vaza."),
    ("EXTORTION", "Aqui e do resgate. Seu sobrinho esta conosco. Deposite agora e nao ligue para ninguem se quiser ve-lo bem."),
    ("EXTORTION", "Voce foi filmado em situacao comprometedora. Evite o vazamento pagando 1.200 via pix em 24 horas."),
    ("EXTORTION", "Seus dados vazaram e estao a venda. Pague a taxa de remocao hoje ou serao usados em crimes no seu nome."),

    # --- TECH_SUPPORT_SCAM (8)
    ("TECH_SUPPORT_SCAM", "Suporte tecnico: seu celular esta infectado. Instale o aplicativo de acesso remoto agora para limpeza gratuita."),
    ("TECH_SUPPORT_SCAM", "Microsoft alerta: licenca expirada e virus detectado. Ligue imediatamente ou compartilhe a tela para correcao."),
    ("TECH_SUPPORT_SCAM", "Sua internet sera cortada por invasao na rede. Baixe nosso app de seguranca e informe a senha do roteador."),
    ("TECH_SUPPORT_SCAM", "Detectamos consumo anormal na sua conta de streaming. Instale a verificacao pelo link e faca login para manter o plano."),
    ("TECH_SUPPORT_SCAM", "Time de seguranca do seu email: acesso critico detectado. Compartilhe a tela agora para removermos o invasor."),
    ("TECH_SUPPORT_SCAM", "Operadora: seu chip sera desativado por erro tecnico. Instale o aplicativo corretor e digite o codigo que aparecer."),
    ("TECH_SUPPORT_SCAM", "Seu backup falhou e as fotos serao apagadas hoje. Acesse a recuperacao urgente e confirme sua senha da nuvem."),
    ("TECH_SUPPORT_SCAM", "Antivirus oficial: pagamento recusado, protecao suspensa. Atualize cartao e senha agora pelo assistente remoto."),

    # --- GOV / órgão público (8) → mapeia para BANK_IMPERSONATION na taxonomia
    ("BANK_IMPERSONATION", "Receita Federal: irregularidade grave no seu CPF. Pague o DARF de regularizacao hoje ou respondera processo."),
    ("BANK_IMPERSONATION", "INSS informa: recadastramento obrigatorio da prova de vida hoje. Confirme dados e senha do gov pelo link."),
    ("BANK_IMPERSONATION", "Justica Eleitoral: seu titulo sera cancelado. Regularize com a taxa expressa agora para nao perder direitos."),
    ("BANK_IMPERSONATION", "Detran: multa gravissima registrada. Pague hoje com 50% de desconto pelo pix da notificacao."),
    ("BANK_IMPERSONATION", "Ministerio da Saude: seu cadastro do SUS expira hoje. Atualize agora informando CPF e senha do aplicativo."),
    ("BANK_IMPERSONATION", "Caixa: seu FGTS tem saque liberado. Antecipe agora pagando a tarifa de processamento pelo link oficial."),
    ("BANK_IMPERSONATION", "Serasa urgente: negativacao entra hoje as 18h. Quite o acordo relampago por pix imediatamente."),
    ("BANK_IMPERSONATION", "Cartorio eletronico: protesto em seu nome sera lavrado hoje. Suste agora com o pagamento da custa avulsa."),

    # --- ROMANCE_OR_EMOTIONAL_MANIPULATION (6)
    ("ROMANCE_OR_EMOTIONAL_MANIPULATION", "Meu amor, finalmente vou te visitar, mas retiveram minha bagagem no aeroporto. Preciso que pague a taxa de 900 agora."),
    ("ROMANCE_OR_EMOTIONAL_MANIPULATION", "Querida, sou militar em missao e nao posso acessar meu banco. Me ajuda com 500 no pix? Confia em mim, te amo."),
    ("ROMANCE_OR_EMOTIONAL_MANIPULATION", "Amor, minha filha adoeceu e estou desesperado. Se voce me ama de verdade, transfere 700 agora, te devolvo em dobro."),
    ("ROMANCE_OR_EMOTIONAL_MANIPULATION", "Voce e a unica pessoa que confio. Meu cartao internacional bloqueou, preciso muito de 350 hoje para o hotel."),
    ("ROMANCE_OR_EMOTIONAL_MANIPULATION", "Nosso encontro depende so dessa taxa do visto. Faz o pix de 1.100 agora, meu bem, e amanha estou ai."),
    ("ROMANCE_OR_EMOTIONAL_MANIPULATION", "Estou preso na alfandega com os presentes que comprei pra voce. Paga a liberacao de 450 agora, por favor, confia em mim."),
]

# (category, text) — mensagens legítimas, incluindo hard negatives
LEGIT: list[tuple[str, str]] = [
    # --- pix legítimo entre conhecidos (20)
    ("pix_legit", "Te mandei o pix do almoco, confere ai se caiu."),
    ("pix_legit", "Acabei de fazer o pix do aluguel pro proprietario, ta pago."),
    ("pix_legit", "Mae, caiu o pix que voce me mandou, obrigado!"),
    ("pix_legit", "Fiz o pix da minha parte do presente da vovo, faltam so o Rafa e a Le."),
    ("pix_legit", "O pedreiro pediu o pagamento por pix, vou pagar amanha de manha."),
    ("pix_legit", "Pode me mandar sua chave pix? Quero te pagar o ingresso de ontem."),
    ("pix_legit", "Recebi seu pix aqui, valeu! Depois te mando o comprovante do boleto."),
    ("pix_legit", "Paguei a diarista por pix hoje, ficou 150 como combinado."),
    ("pix_legit", "Filha, seu pai fez o pix da faculdade hoje cedo, confirma com a secretaria."),
    ("pix_legit", "Dividi a conta no pix, cada um ficou 42,50. Ja te mandei o valor."),
    ("pix_legit", "O condominio agora aceita pix, bem mais facil que boleto."),
    ("pix_legit", "Consegui transferir pelo pix mesmo, o TED estava fora do ar."),
    ("pix_legit", "Vou te devolver os 200 por pix na sexta quando cair meu salario, ok?"),
    ("pix_legit", "A costureira cobrou 80 pela barra, ja deixei pago no pix dela."),
    ("pix_legit", "Manda o pix pra chave do CPF da mamae mesmo, ela ja confirmou."),
    ("pix_legit", "Pix recebido! Amanha levo as verduras da feira pra senhora."),
    ("pix_legit", "Lembra de pagar o gas hoje, o rapaz aceita pix na entrega."),
    ("pix_legit", "Fiz um pix errado de 10 reais pro seu numero antigo ontem, depois me devolve sem pressa."),
    ("pix_legit", "O aluguel da quadra deu 120, fiz o pix e ja reservei nosso horario."),
    ("pix_legit", "Sobrinha, seu tio mandou um pix de presente de aniversario, olha o app."),

    # --- coordenação de pagamentos legítima (15)
    ("payment_legit", "Nao esquece do boleto da escola que vence sexta, ta na mesa da cozinha."),
    ("payment_legit", "Paguei a conta de luz hoje, deu 187 esse mes por causa do ar."),
    ("payment_legit", "A parcela do carro cai dia 10, ja deixei o dinheiro separado na conta."),
    ("payment_legit", "Transferi sua mesada, filho. Usa com juizo essa semana."),
    ("payment_legit", "O dentista parcelou em 3x, primeira parcela so mes que vem."),
    ("payment_legit", "Consegui desconto de 10% pagando a anuidade a vista, ja quitei."),
    ("payment_legit", "Amor, paga o IPTU pelo app quando puder, o codigo ta no email."),
    ("payment_legit", "A fatura do cartao veio 620 esse mes, dentro do esperado."),
    ("payment_legit", "Recebi o reembolso do plano de saude hoje, caiu certinho."),
    ("payment_legit", "Vou pagar a metade da viagem agora e o resto em janeiro, combinado com a agencia."),
    ("payment_legit", "O mercado tava com promocao, gastei 230 na compra do mes."),
    ("payment_legit", "Lembrete: amanha vence a mensalidade do judo do Pedro."),
    ("payment_legit", "Ja acertei com o sindico a taxa extra da pintura, ficou 45 por apartamento."),
    ("payment_legit", "Meu salario caiu hoje, vou adiantar as contas do mes a tarde."),
    ("payment_legit", "A oficina cobrou 380 na revisao, te mando o comprovante quando pagar."),

    # --- senha/código em contexto benigno (15)
    ("password_benign", "A senha do wifi de casa e familia2020, com f minusculo."),
    ("password_benign", "Esqueci minha senha do email de novo, vou ter que redefinir kkk."),
    ("password_benign", "Troquei a senha do portao eletronico, te falo pessoalmente qual e."),
    ("password_benign", "O codigo do armario da academia e o mesmo do mes passado."),
    ("password_benign", "Filha, como faco pra mudar a senha do meu celular? Me ensina domingo."),
    ("password_benign", "A professora mandou o codigo da turma do aplicativo da escola no grupo."),
    ("password_benign", "Anota a senha do streaming: a mesma de sempre com 2024 no final."),
    ("password_benign", "Nao consigo lembrar a senha do banco, amanha vou na agencia redefinir pessoalmente."),
    ("password_benign", "O tecnico veio aqui e trocou a senha do roteador, ta atras do aparelho."),
    ("password_benign", "Chegou o codigo de rastreio da encomenda no meu email, a previsao e quinta."),
    ("password_benign", "Meu token do trabalho travou, vou chamar o TI segunda-feira."),
    ("password_benign", "Configurei senha nova no tablet da vovo, deixei anotada na agenda dela."),
    ("password_benign", "O cadeado da bicicleta usa codigo, e o ano que voce nasceu."),
    ("password_benign", "Ativei a senha de dois fatores no meu email como voce recomendou."),
    ("password_benign", "A senha do cofre do hotel a gente escolhe na hora do check-in."),

    # --- urgência benigna (15)
    ("urgency_benign", "Urgente: a reuniao mudou pra 14h, avisa o pessoal da equipe."),
    ("urgency_benign", "Corre aqui em casa agora, o jogo ja vai comecar!"),
    ("urgency_benign", "Mae, vem rapido que o bolo ta saindo do forno agora."),
    ("urgency_benign", "Preciso muito da sua ajuda com a mudanca no sabado, posso contar contigo?"),
    ("urgency_benign", "Sai agora do trabalho, chego em 40 minutos pra jantar."),
    ("urgency_benign", "Emergencia boa: sobrou um ingresso pro show de hoje, topa?"),
    ("urgency_benign", "Responde rapido: pizza ou hamburguer pro jantar de hoje?"),
    ("urgency_benign", "O onibus adiantou, to chegando agora na rodoviaria."),
    ("urgency_benign", "Avisa a vo que saimos agora e chegamos pro almoco."),
    ("urgency_benign", "Urgente pra ontem: preciso do numero do sapato do papai pro presente."),
    ("urgency_benign", "A consulta foi antecipada pra hoje as 16h, consegue me levar?"),
    ("urgency_benign", "Liga pra farmacia agora antes que feche, o remedio chegou."),
    ("urgency_benign", "Vaga na garagem liberada agora, desce logo antes que ocupem."),
    ("urgency_benign", "Ta chovendo muito, recolhe a roupa do varal agora por favor."),
    ("urgency_benign", "Prova amanha cedo, me liga urgente pra revisarmos juntos hoje."),

    # --- links benignos (15)
    ("link_benign", "Olha esse video que a Duda mandou, muito engracado: https://youtube.com/watch?v=abc123"),
    ("link_benign", "Segue a localizacao do restaurante no maps: https://maps.google.com/?q=cantina+da+nonna"),
    ("link_benign", "A receita do bolo de cenoura que voce pediu: www.tudogostoso.com.br/receita/23-bolo-de-cenoura"),
    ("link_benign", "Materia interessante sobre o bairro: https://g1.globo.com/sp/noticia/revitalizacao-centro"),
    ("link_benign", "O link da reuniao de amanha e esse: https://meet.google.com/abc-defg-hij"),
    ("link_benign", "Criei o album das fotos da viagem, olha que lindo: https://photos.app.goo.gl/xyz"),
    ("link_benign", "O edital do concurso saiu, ta aqui: www.prefeitura.sp.gov.br/editais"),
    ("link_benign", "Manda esse link do curriculo pro seu primo: https://linkedin.com/in/maria-silva"),
    ("link_benign", "Playlist pro churrasco de domingo: https://open.spotify.com/playlist/churrasco2026"),
    ("link_benign", "A live da igreja comeca 19h nesse link de sempre do canal."),
    ("link_benign", "Comprei nesse site que voce indicou, chegou rapidinho mesmo: www.magazineluiza.com.br"),
    ("link_benign", "Olha o trailer do filme que estreia sexta: https://youtube.com/watch?v=trailer2026"),
    ("link_benign", "O grupo da familia agora tem link de convite, te mandei no privado."),
    ("link_benign", "Baixa o app da farmacia pelo site oficial que tem cupom de primeira compra."),
    ("link_benign", "Segue o link do formulario da festa junina da escola: https://forms.gle/festajunina"),

    # --- conversa cotidiana (25)
    ("small_talk", "Oi, tudo bem? Bom dia!"),
    ("small_talk", "Cheguei bem em casa, pode ficar tranquila."),
    ("small_talk", "Que saudade de voces, quando vem visitar a gente?"),
    ("small_talk", "O almoco de domingo ta de pe? Levo a sobremesa."),
    ("small_talk", "Feliz aniversario, titia! Muita saude e alegria!"),
    ("small_talk", "Viu o jogo ontem? Que golaco no final, nao acreditei."),
    ("small_talk", "A Bela tirou 9,5 na prova de matematica, ta toda orgulhosa."),
    ("small_talk", "Choveu demais aqui hoje, ate alagou a rua de baixo."),
    ("small_talk", "Vou fazer aquele frango assado que voce gosta no domingo."),
    ("small_talk", "O medico disse que a pressao ta otima, exame tudo normal."),
    ("small_talk", "Boa noite, durma bem, amanha te ligo cedinho."),
    ("small_talk", "Kkkkk essa foto do cachorro de oculos me matou de rir."),
    ("small_talk", "A novela de ontem foi de chorar, voce assistiu?"),
    ("small_talk", "Meu joelho ta bem melhor com a fisioterapia, obrigada por perguntar."),
    ("small_talk", "Passei no mercado e comprei aquele cafe que voce ama."),
    ("small_talk", "As criancas mandaram beijo pra vovo, tao com saudade."),
    ("small_talk", "Domingo tem feira de artesanato na praca, bora dar uma volta?"),
    ("small_talk", "Terminei o livro que voce emprestou, maravilhoso, obrigada!"),
    ("small_talk", "O vizinho novo e gente boa, ja se apresentou pra todo mundo."),
    ("small_talk", "Consegui a receita do pao de queijo da Dona Cida, e segredo de familia!"),
    ("small_talk", "Hoje faz 40 anos que seu avo me pediu em casamento."),
    ("small_talk", "A missa de setimo dia do seu Antonio e sabado as 10h."),
    ("small_talk", "Plantei tomate na horta, se der certo te dou uma muda."),
    ("small_talk", "O gato aprendeu a abrir a porta da cozinha, acredita?"),
    ("small_talk", "Voltei da caminhada agora, 5km hoje, to me sentindo otima."),

    # --- trabalho (15)
    ("work", "A reuniao de alinhamento ficou pra quinta as 10h na sala 3."),
    ("work", "Consegue revisar o relatorio ate amanha cedo? Sem pressa hoje."),
    ("work", "O cliente aprovou a proposta, comecamos na segunda!"),
    ("work", "Vou chegar 15 minutos atrasado, o transito ta parado na marginal."),
    ("work", "Lembrete: entrega do projeto e sexta-feira ate as 18h."),
    ("work", "O RH confirmou suas ferias de 10 a 24 de agosto."),
    ("work", "Feedback do chefe foi otimo, parabens pela apresentacao!"),
    ("work", "Home office liberado na sexta por causa da manutencao do predio."),
    ("work", "A impressora do terceiro andar voltou a funcionar."),
    ("work", "Confirma presenca no treinamento de seguranca de terca?"),
    ("work", "Nosso fornecedor atrasou a entrega, replanejei o cronograma."),
    ("work", "A vaga de analista foi aberta internamente, se inscreve!"),
    ("work", "Ata da reuniao enviada por email, qualquer ajuste me avisa."),
    ("work", "O estagiario novo comeca amanha, vamos almocar todos juntos?"),
    ("work", "Sistema fica fora do ar domingo das 2h as 6h pra manutencao."),

    # --- contas legítimas (10)
    ("bills_legit", "Chegou a conta de agua, 68 reais, vence dia 15."),
    ("bills_legit", "O boleto do curso de ingles chegou por email, mesma coisa de sempre."),
    ("bills_legit", "Renovei o seguro do carro, parcelei em 10x sem juros."),
    ("bills_legit", "A mensalidade da natacao aumentou 5% esse ano, aviso oficial no mural."),
    ("bills_legit", "Paguei o boleto do material escolar hoje na lotérica."),
    ("bills_legit", "Nossa conta de internet veio errada, liguei e ja corrigiram pra proxima."),
    ("bills_legit", "O IPVA desse ano da pra pagar em 3 parcelas comecando em fevereiro."),
    ("bills_legit", "Assinei o jornal digital, 12,90 por mes no cartao."),
    ("bills_legit", "A academia mandou o reajuste anual por email, subiu 8 reais."),
    ("bills_legit", "Conta de luz de janeiro veio mais alta como sempre no verao."),

    # --- entregas legítimas (10)
    ("delivery_legit", "Seu pedido da farmacia ta comigo na portaria, desce quando puder."),
    ("delivery_legit", "A encomenda que voce esperava chegou aqui em casa, ta guardada."),
    ("delivery_legit", "O rastreio diz que o livro chega quinta-feira."),
    ("delivery_legit", "Entregador do mercado chegou, ja recebi as compras."),
    ("delivery_legit", "Deixei seu pacote com a vizinha do 42 como voce pediu."),
    ("delivery_legit", "A transportadora ligou confirmando entrega da geladeira amanha de manha."),
    ("delivery_legit", "Pedido saiu para entrega segundo o app, deve chegar na hora do almoco."),
    ("delivery_legit", "Retirei sua encomenda nos correios com a autorizacao que voce mandou."),
    ("delivery_legit", "O motoboy do restaurante ja ta descendo a rua, prepara a mesa!"),
    ("delivery_legit", "As flores que voce mandou pra mamae chegaram, ela amou!"),

    # --- assuntos de banco legítimos (10)
    ("bank_legit", "Fui no banco hoje resolver aquilo do cartao, tudo certo agora."),
    ("bank_legit", "Minha gerente confirmou que o financiamento foi aprovado, assino sexta."),
    ("bank_legit", "O banco vai fechar mais cedo na vespera de feriado, se programa."),
    ("bank_legit", "Atualizei meu cadastro presencialmente na agencia como pediram por carta."),
    ("bank_legit", "Consegui isencao da tarifa da conta conversando com o gerente."),
    ("bank_legit", "O caixa eletronico do shopping ta em manutencao, usa o da esquina."),
    ("bank_legit", "Abri uma poupanca pra Alice, deposito 50 todo mes."),
    ("bank_legit", "Meu cartao novo chegou pelo correio, o antigo ja cancelei no app."),
    ("bank_legit", "A agencia mudou o horario de atendimento, agora abre as 10h."),
    ("bank_legit", "Recebi o extrato anual pra declaracao do imposto de renda."),

    # --- logística de família (5)
    ("family_logistics", "Busco as criancas na escola hoje, pode deixar."),
    ("family_logistics", "Consulta da vovo remarcada pra quarta as 9h, anota ai."),
    ("family_logistics", "Levei o carro pro mecanico, fica pronto sexta."),
    ("family_logistics", "A chave reserva ta com a Dona Neusa do 101."),
    ("family_logistics", "Remedio da pressao ta acabando, compro amanha na promocao."),
]


def entries():
    """Yield dicts: {id, label, category, text}."""
    for i, (scam_type, text) in enumerate(SCAM, start=1):
        yield {"id": f"s{i:03d}", "label": "scam", "category": scam_type, "text": text}
    for i, (category, text) in enumerate(LEGIT, start=1):
        yield {"id": f"l{i:03d}", "label": "legit", "category": category, "text": text}
