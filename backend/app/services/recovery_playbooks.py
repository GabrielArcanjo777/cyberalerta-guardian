from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from app.schemas.recovery import RecoveryPlanStep, RecoveryRequest, RecoveryResponse

INCIDENT_TYPES = {
    "pix_sent",
    "suspicious_link_clicked",
    "sms_code_shared",
    "password_shared",
    "remote_app_installed",
    "job_fee_paid",
    "unknown",
}

DISCLAIMER = (
    "Este plano e uma orientacao inicial de seguranca, nao substitui atendimento do banco, suporte oficial "
    "ou orientacao juridica. Nao ha garantia de recuperacao de valores."
)


@dataclass(frozen=True)
class RecoveryPlaybook:
    incident_type: str
    severity: str
    summary: str
    immediate_steps: tuple[str, ...]
    next_24h_steps: tuple[str, ...]
    evidence_to_collect: tuple[str, ...]
    contacts_to_notify: tuple[str, ...]
    do_not_do: tuple[str, ...]
    accounts_to_secure: tuple[str, ...]


PLAYBOOKS: dict[str, RecoveryPlaybook] = {
    "pix_sent": RecoveryPlaybook(
        incident_type="pix_sent",
        severity="critical",
        summary="Pagamento Pix ou transferencia ja realizada com sinais de golpe.",
        immediate_steps=(
            "Contactar instituicao financeira imediatamente.",
            "Pedir contestacao da transacao e perguntar sobre bloqueio ou devolucao disponivel.",
            "Nao enviar mais dinheiro, mesmo que a pessoa insista ou prometa resolver.",
        ),
        next_24h_steps=(
            "Registrar ocorrencia de fraude e bloquear transacao.",
            "Guardar comprovante, chave Pix, conversa e dados publicos do recebedor.",
            "Acompanhar resposta do banco por canal oficial.",
        ),
        evidence_to_collect=(
            "Comprovante do Pix ou transferencia.",
            "Prints da conversa e perfil que fez o pedido.",
            "Data, horario, valor, chave Pix e identificador da transacao.",
        ),
        contacts_to_notify=(
            "Banco ou instituicao financeira pelo canal oficial.",
            "Contato de confianca ou familiar responsavel.",
            "Canal oficial de ocorrencia, se a pessoa decidir registrar.",
        ),
        do_not_do=(
            "Nao pagar nova taxa para tentar recuperar o valor.",
            "Nao negociar com o suspeito fora de canal oficial.",
            "Nao compartilhar senha, codigo ou documento para terceiros.",
        ),
        accounts_to_secure=("Conta bancaria", "E-mail vinculado ao banco", "WhatsApp"),
    ),
    "suspicious_link_clicked": RecoveryPlaybook(
        incident_type="suspicious_link_clicked",
        severity="high",
        summary="Link suspeito foi acessado e pode ter coletado dados ou iniciado login falso.",
        immediate_steps=(
            "Parar de interagir com o site ou conversa imediatamente.",
            "Trocar senhas importantes em um dispositivo seguro.",
            "Ativar verificacao em duas etapas nas contas principais.",
        ),
        next_24h_steps=(
            "Revisar sessoes conectadas e encerrar acessos desconhecidos.",
            "Monitorar banco, e-mail e contas usadas no link.",
            "Salvar o link e prints para verificacao posterior.",
        ),
        evidence_to_collect=(
            "URL do link suspeito.",
            "Print da tela acessada.",
            "Horario aproximado do clique e dados informados, sem repetir senha em mensagens.",
        ),
        contacts_to_notify=(
            "Suporte oficial do servico afetado.",
            "Contato de confianca.",
        ),
        do_not_do=(
            "Nao inserir novos dados no link.",
            "Nao baixar arquivos adicionais.",
            "Nao reaproveitar a mesma senha em outras contas.",
        ),
        accounts_to_secure=("E-mail", "Banco", "Redes sociais", "WhatsApp"),
    ),
    "sms_code_shared": RecoveryPlaybook(
        incident_type="sms_code_shared",
        severity="critical",
        summary="Codigo, token ou OTP foi compartilhado com terceiro.",
        immediate_steps=(
            "Trocar a senha do servico afetado por canal oficial.",
            "Revogar sessoes abertas e dispositivos desconhecidos.",
            "Ativar ou revisar a verificacao em duas etapas.",
        ),
        next_24h_steps=(
            "Avisar o suporte oficial do servico afetado.",
            "Monitorar tentativas de login e mudancas de dados cadastrais.",
            "Verificar se e-mail e telefone de recuperacao foram alterados.",
        ),
        evidence_to_collect=(
            "Print da mensagem que pediu o codigo.",
            "Horario em que o codigo foi compartilhado.",
            "Nome do servico relacionado ao codigo.",
        ),
        contacts_to_notify=(
            "Suporte oficial do servico afetado.",
            "Contato de confianca.",
        ),
        do_not_do=(
            "Nao compartilhar novo codigo recebido.",
            "Nao confirmar notificacoes de login que voce nao iniciou.",
            "Nao passar senha ou documento para recuperar acesso por chat desconhecido.",
        ),
        accounts_to_secure=("Conta afetada", "E-mail de recuperacao", "WhatsApp"),
    ),
    "password_shared": RecoveryPlaybook(
        incident_type="password_shared",
        severity="critical",
        summary="Senha foi compartilhada ou digitada em ambiente suspeito.",
        immediate_steps=(
            "Trocar a senha imediatamente em um dispositivo seguro.",
            "Encerrar sessoes abertas em aparelhos desconhecidos.",
            "Ativar verificacao em duas etapas.",
        ),
        next_24h_steps=(
            "Trocar senhas repetidas em outros servicos.",
            "Verificar e-mail, banco e redes sociais por mudancas nao reconhecidas.",
            "Salvar evidencias da conversa ou pagina que solicitou a senha.",
        ),
        evidence_to_collect=(
            "Print da solicitacao da senha.",
            "Servico ou conta onde a senha foi usada.",
            "Horario aproximado do compartilhamento.",
        ),
        contacts_to_notify=(
            "Suporte oficial do servico afetado.",
            "Contato de confianca.",
        ),
        do_not_do=(
            "Nao repetir a senha antiga.",
            "Nao enviar senha por mensagem.",
            "Nao usar link recebido para redefinir senha se ele parecer suspeito.",
        ),
        accounts_to_secure=("E-mail principal", "Banco", "Redes sociais", "Conta afetada"),
    ),
    "remote_app_installed": RecoveryPlaybook(
        incident_type="remote_app_installed",
        severity="critical",
        summary="Aplicativo remoto ou desconhecido foi instalado durante a abordagem.",
        immediate_steps=(
            "Desconectar o aparelho da internet se houver suspeita de controle remoto.",
            "Desinstalar o aplicativo remoto ou desconhecido.",
            "Trocar senhas em outro dispositivo seguro.",
        ),
        next_24h_steps=(
            "Revisar permissoes de aplicativos instalados.",
            "Contatar banco por canal oficial para revisar movimentacoes.",
            "Considerar verificacao tecnica do aparelho antes de voltar a usar apps sensiveis.",
        ),
        evidence_to_collect=(
            "Nome do aplicativo instalado.",
            "Prints das instrucoes recebidas.",
            "Horario de instalacao e permissoes concedidas.",
        ),
        contacts_to_notify=(
            "Banco ou instituicao financeira.",
            "Contato de confianca.",
            "Suporte tecnico confiavel.",
        ),
        do_not_do=(
            "Nao abrir app bancario no aparelho suspeito.",
            "Nao permitir novo acesso remoto.",
            "Nao digitar senhas enquanto houver suspeita de controle externo.",
        ),
        accounts_to_secure=("Banco", "E-mail", "WhatsApp", "Conta do aparelho"),
    ),
    "job_fee_paid": RecoveryPlaybook(
        incident_type="job_fee_paid",
        severity="high",
        summary="Taxa de vaga, treinamento ou falso emprego foi paga ou solicitada.",
        immediate_steps=(
            "Parar novos pagamentos imediatamente.",
            "Guardar comprovantes, conversas e dados publicos do perfil ou empresa.",
            "Confirmar a empresa por canais oficiais fora da conversa suspeita.",
        ),
        next_24h_steps=(
            "Avisar a plataforma onde a vaga apareceu, se houver.",
            "Consultar o banco sobre contestacao ou medidas disponiveis.",
            "Registrar ocorrencia se a pessoa decidir formalizar o caso.",
        ),
        evidence_to_collect=(
            "Comprovante de pagamento da taxa.",
            "Print da vaga, perfil, conversa e promessa feita.",
            "Nome usado pela suposta empresa e dados de contato informados.",
        ),
        contacts_to_notify=(
            "Banco ou meio de pagamento.",
            "Plataforma de vagas ou rede social.",
            "Contato de confianca.",
        ),
        do_not_do=(
            "Nao pagar taxa extra para liberar vaga ou reembolso.",
            "Nao enviar documentos adicionais sem verificar a empresa.",
            "Nao instalar aplicativos pedidos pela conversa suspeita.",
        ),
        accounts_to_secure=("E-mail", "Conta da plataforma de vagas", "Banco"),
    ),
    "unknown": RecoveryPlaybook(
        incident_type="unknown",
        severity="medium",
        summary="Incidente ainda nao classificado, mas com necessidade de pausa e verificacao.",
        immediate_steps=(
            "Parar a conversa e nao tomar novas acoes por enquanto.",
            "Guardar prints e informacoes publicas do contato.",
            "Pedir ajuda a um contato de confianca para revisar o caso.",
        ),
        next_24h_steps=(
            "Verificar pelos canais oficiais antes de pagar, clicar ou informar dados.",
            "Monitorar contas importantes se algum dado foi compartilhado.",
            "Atualizar o caso com novas informacoes se surgirem.",
        ),
        evidence_to_collect=(
            "Prints da conversa.",
            "Numero, perfil ou link usado pelo contato.",
            "Resumo do que foi pedido.",
        ),
        contacts_to_notify=("Contato de confianca.",),
        do_not_do=(
            "Nao pagar valores adicionais.",
            "Nao clicar em links recebidos na conversa suspeita.",
            "Nao compartilhar senha, codigo ou documento.",
        ),
        accounts_to_secure=("E-mail", "WhatsApp"),
    ),
}


def build_recovery_response(request: RecoveryRequest) -> RecoveryResponse:
    incident_type = infer_incident_type(request)
    playbook = PLAYBOOKS[incident_type]
    immediate_steps = list(playbook.immediate_steps)
    next_24h_steps = list(playbook.next_24h_steps)
    evidence = list(playbook.evidence_to_collect)

    if request.shared_documents and "Documentos enviados, se houver." not in evidence:
        evidence.append("Documentos enviados, se houver.")

    summary = _summary_with_context(playbook.summary, request)
    checklist = _legacy_checklist(playbook, request, immediate_steps, next_24h_steps)
    whatsapp_steps = _whatsapp_step_messages(playbook, immediate_steps, next_24h_steps)

    return RecoveryResponse(
        checklist=checklist,
        incident_type=incident_type,
        severity=playbook.severity,
        summary=summary,
        immediate_steps=immediate_steps,
        next_24h_steps=next_24h_steps,
        evidence_to_collect=evidence,
        contacts_to_notify=list(playbook.contacts_to_notify),
        do_not_do=list(playbook.do_not_do),
        whatsapp_summary_message=_whatsapp_summary(playbook, summary),
        whatsapp_step_messages=whatsapp_steps,
        trusted_contact_message=_trusted_contact_message(playbook, request),
        report_summary=_report_summary(playbook, request),
        disclaimer=DISCLAIMER,
        n8n_action=f"send_recovery_{incident_type}",
        case_id=request.case_id,
        n8n_execution_id=request.n8n_execution_id,
        recovery_plan=_recovery_plan_steps(immediate_steps, next_24h_steps),
        evidence_to_save=evidence,
        accounts_to_secure=list(playbook.accounts_to_secure),
        what_not_to_do=list(playbook.do_not_do),
    )


def infer_incident_type(request: RecoveryRequest) -> str:
    explicit = str(request.incident_type or "").strip().lower()
    if explicit in INCIDENT_TYPES:
        return explicit
    if request.has_installed_remote_app is True or request.installed_app:
        return "remote_app_installed"
    if request.has_sent_code is True or request.shared_sms_code:
        return "sms_code_shared"
    if request.has_shared_password is True or request.shared_password:
        return "password_shared"
    if request.has_clicked_link is True or request.clicked_link:
        return "suspicious_link_clicked"
    source = str(request.source or "").lower()
    if request.paid or request.already_paid is True:
        if "emprego" in source or "job" in source or "vaga" in source:
            return "job_fee_paid"
        return "pix_sent"
    return "unknown"


def _legacy_checklist(
    playbook: RecoveryPlaybook,
    request: RecoveryRequest,
    immediate_steps: Iterable[str],
    next_24h_steps: Iterable[str],
) -> list[str]:
    checklist = [*immediate_steps, *next_24h_steps]
    legacy_steps = []
    if request.paid or request.already_paid is True:
        legacy_steps.append("Contactar instituicao financeira imediatamente.")
        legacy_steps.append("Registrar ocorrencia de fraude e bloquear transacao.")
    if request.clicked_link:
        legacy_steps.append("Nao acesse o link novamente e verifique se ha malware.")
    if request.shared_password:
        legacy_steps.append("Altere senhas e ative autenticacao de dois fatores.")
    if request.installed_app:
        legacy_steps.append("Desinstale o app remoto e execute analise de seguranca.")
    if request.shared_sms_code:
        legacy_steps.append("Notifique prestador de servico e bloqueie acessos por SMS.")
    if request.shared_documents:
        legacy_steps.append("Verifique se documentos enviados podem ter sido usados indevidamente.")
    for step in legacy_steps:
        if step not in checklist:
            checklist.append(step)
    if not checklist:
        return ["Nenhuma acao de risco confirmada. Monitore e informe familiares."]
    if playbook.incident_type == "unknown":
        checklist.append("Nenhuma acao de risco confirmada. Monitore e informe familiares.")
    return checklist


def _recovery_plan_steps(immediate_steps: list[str], next_24h_steps: list[str]) -> list[RecoveryPlanStep]:
    plan: list[RecoveryPlanStep] = []
    for index, step in enumerate(immediate_steps, start=1):
        plan.append(
            RecoveryPlanStep(
                priority=f"agora-{index}",
                title="Acao imediata",
                description=step,
                category="immediate",
            )
        )
    for index, step in enumerate(next_24h_steps, start=1):
        plan.append(
            RecoveryPlanStep(
                priority=f"24h-{index}",
                title="Proximas 24h",
                description=step,
                category="next_24h",
            )
        )
    return plan


def _summary_with_context(summary: str, request: RecoveryRequest) -> str:
    details: list[str] = []
    if request.amount is not None:
        details.append(f"valor informado: R$ {request.amount:.2f}")
    if request.payment_method:
        details.append(f"metodo: {request.payment_method}")
    if request.bank_name:
        details.append(f"banco: {request.bank_name}")
    if not details:
        return summary
    return f"{summary} Contexto: {', '.join(details)}."


def _whatsapp_summary(playbook: RecoveryPlaybook, summary: str) -> str:
    return (
        f"Guardian Recovery: {summary} Vou te passar passos curtos. "
        "Nao envie mais dinheiro, senhas ou codigos enquanto verifica por canais oficiais."
    )


def _whatsapp_step_messages(
    playbook: RecoveryPlaybook,
    immediate_steps: list[str],
    next_24h_steps: list[str],
) -> list[str]:
    messages = [f"Passo {index}: {step}" for index, step in enumerate(immediate_steps, start=1)]
    if next_24h_steps:
        messages.append(f"Depois: {next_24h_steps[0]}")
    messages.append(DISCLAIMER)
    return messages


def _trusted_contact_message(playbook: RecoveryPlaybook, request: RecoveryRequest) -> str:
    case_text = f" Caso: {request.case_id}." if request.case_id else ""
    return (
        f"Alerta Guardian Recovery: incidente {playbook.incident_type} com severidade {playbook.severity}. "
        f"Ajude a pessoa a pausar novas acoes e seguir canais oficiais.{case_text}"
    )


def _report_summary(playbook: RecoveryPlaybook, request: RecoveryRequest) -> str:
    case_text = f" Case ID: {request.case_id}." if request.case_id else ""
    return (
        f"Recovery iniciado para {playbook.incident_type}. Severidade: {playbook.severity}. "
        f"Plano: acoes imediatas, proximas 24h, evidencias e contatos oficiais.{case_text}"
    )
