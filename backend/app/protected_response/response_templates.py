from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class ResponseTemplate:
    high_risk: str
    medium_risk: str
    low_risk: str
    do_not_do: List[str]
    next_step_high: str
    next_step_low: str


TEMPLATES = {
    "golpe_pix": ResponseTemplate(
        high_risk=(
            "Não faça Pix agora. Essa mensagem tem sinais de golpe{contact_suffix}."
        ),
        medium_risk=(
            "Espere antes de fazer Pix. Há sinais de risco nessa mensagem{contact_suffix}."
        ),
        low_risk=(
            "Recebi sua mensagem. Não faça nenhuma transferência urgente agora{contact_suffix}."
        ),
        do_not_do=["não fazer Pix", "não clicar", "não enviar código"],
        next_step_high="aguardar contato de confiança",
        next_step_low="aguardar verificação",
    ),
    "link_suspeito": ResponseTemplate(
        high_risk=(
            "Não clique nesse link. Ele pode ser perigoso{verify_suffix}."
        ),
        medium_risk=(
            "Não abra esse link ainda. Peça confirmação antes de clicar{verify_suffix}."
        ),
        low_risk=(
            "Recebi sua mensagem. Evite clicar em links desconhecidos por enquanto{verify_suffix}."
        ),
        do_not_do=["não clicar", "não instalar app", "não enviar dados"],
        next_step_high="aguardar contato de confiança",
        next_step_low="aguardar verificação",
    ),
    "codigo_senha": ResponseTemplate(
        high_risk=(
            "Não envie código nem senha. Aguarde{contact_wait}."
        ),
        medium_risk=(
            "Não compartilhe códigos ou senhas. Confirme com alguém de confiança antes{contact_wait}."
        ),
        low_risk=(
            "Recebi sua mensagem. Não envie códigos ou senhas por mensagem{contact_wait}."
        ),
        do_not_do=["não enviar código", "não enviar senha", "não instalar app remoto"],
        next_step_high="aguardar contato de confiança",
        next_step_low="aguardar verificação",
    ),
    "falso_banco": ResponseTemplate(
        high_risk=(
            "Não continue a conversa. Use apenas o canal oficial do banco{or_responsible}."
        ),
        medium_risk=(
            "Não siga instruções dessa mensagem. Confirme no app ou site oficial do banco{or_responsible}."
        ),
        low_risk=(
            "Recebi sua mensagem. Confirme sempre pelo canal oficial do banco{or_responsible}."
        ),
        do_not_do=["não clicar em links", "não informar senha", "não fazer Pix"],
        next_step_high="aguardar contato de confiança",
        next_step_low="aguardar verificação",
    ),
    "risco_baixo": ResponseTemplate(
        high_risk=(
            "Recebi sua mensagem. Não faça nenhuma ação urgente agora{contact_suffix}."
        ),
        medium_risk=(
            "Recebi sua mensagem. Não faça nenhuma ação urgente agora{contact_suffix}."
        ),
        low_risk=(
            "Recebi sua mensagem. Vou registrar para verificação, mas não faça nenhuma ação urgente agora."
        ),
        do_not_do=["não agir com pressa"],
        next_step_high="aguardar verificação",
        next_step_low="aguardar verificação",
    ),
    "generico": ResponseTemplate(
        high_risk=(
            "Não siga essa solicitação agora. Há sinais de risco{contact_suffix}."
        ),
        medium_risk=(
            "Espere um instante. Confirme por outro canal antes de agir{contact_suffix}."
        ),
        low_risk=(
            "Recebi sua mensagem. Não faça nenhuma ação urgente agora{contact_suffix}."
        ),
        do_not_do=["não clicar", "não enviar dados sensíveis"],
        next_step_high="aguardar contato de confiança",
        next_step_low="aguardar verificação",
    ),
}


def contact_suffix(alias: Optional[str], high_risk: bool) -> str:
    if alias:
        if high_risk:
            return f" e estou avisando {alias}"
        return f"; {alias} pode ajudar a confirmar"
    if high_risk:
        return " e seu contato de confiança será avisado"
    return ""


def verify_suffix(alias: Optional[str], high_risk: bool) -> str:
    if alias and high_risk:
        return f" e o caso será verificado com {alias}"
    if high_risk:
        return " e o caso será verificado pelo responsável"
    return ""


def contact_wait(alias: Optional[str]) -> str:
    if alias:
        return f" até {alias} confirmar"
    return " seu contato de confiança confirmar"


def or_responsible(alias: Optional[str]) -> str:
    if alias:
        return f" ou aguarde {alias}"
    return " ou aguarde seu responsável"
