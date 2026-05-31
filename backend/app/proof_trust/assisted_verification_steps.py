from __future__ import annotations

from copy import deepcopy
from typing import List, Literal, TypedDict

StepStatus = Literal["pending", "completed", "skipped"]


class StepDefinition(TypedDict):
    id: str
    title: str
    guidance: str


VERIFICATION_STEP_DEFINITIONS: List[StepDefinition] = [
    {
        "id": "do_not_reply",
        "title": "Não responder ao contato suspeito",
        "guidance": "Não use o contato suspeito como fonte de verificação. Evite clicar, ligar de volta ou enviar dados.",
    },
    {
        "id": "confirm_independent_channel",
        "title": "Confirmar pelo contato salvo",
        "guidance": "Confirme por canal independente — telefone salvo, visita presencial ou contato já conhecido.",
    },
    {
        "id": "identity_challenge",
        "title": "Pergunta combinada",
        "guidance": "Faça uma pergunta que só a pessoa real saberia responder (combinada previamente com a família).",
    },
    {
        "id": "confirm_request_real",
        "title": "Confirmar se o pedido é real",
        "guidance": "Confirme se o pedido financeiro ou a ação solicitada é real — sem usar o número ou link suspeito.",
    },
    {
        "id": "record_decision",
        "title": "Registrar decisão",
        "guidance": "Registre o resultado da verificação para auditoria do caso (demo — sem CPF ou documentos).",
    },
    {
        "id": "release_or_block",
        "title": "Liberar somente após confirmação",
        "guidance": "Liberar ação apenas se verificado seguro; caso contrário, manter pausa protetiva (Trust Lock).",
    },
]

AUTO_COMPLETED_ON_START = {"do_not_reply"}


def build_initial_steps() -> List[dict]:
    steps: List[dict] = []
    for definition in VERIFICATION_STEP_DEFINITIONS:
        step_id = definition["id"]
        status: StepStatus = "completed" if step_id in AUTO_COMPLETED_ON_START else "pending"
        steps.append(
            {
                "id": step_id,
                "title": definition["title"],
                "status": status,
                "guidance": definition["guidance"],
                "note": None,
            }
        )
    return steps


def current_step_id(steps: List[dict]) -> str:
    for step in steps:
        if step["status"] == "pending":
            return step["id"]
    return "release_or_block"


def all_steps_completed(steps: List[dict]) -> bool:
    return all(step["status"] in {"completed", "skipped"} for step in steps)


def get_step_definition(step_id: str) -> StepDefinition | None:
    for definition in VERIFICATION_STEP_DEFINITIONS:
        if definition["id"] == step_id:
            return definition
    return None


def validate_step_id(step_id: str) -> bool:
    return get_step_definition(step_id) is not None
