from app.schemas.recovery import RecoveryRequest, RecoveryResponse


class RecoveryAgent:
    def analyze(self, request: RecoveryRequest) -> RecoveryResponse:
        checklist = []
        if request.paid:
            checklist.append("Contactar instituicao financeira imediatamente.")
            checklist.append("Registrar ocorrencia de fraude e bloquear transacao.")
        if request.clicked_link:
            checklist.append("Nao acesse o link novamente e verifique se ha malware.")
        if request.shared_documents:
            checklist.append("Verifique se documentos enviados podem ter sido usados indevidamente.")
        if request.shared_password:
            checklist.append("Altere senhas e ative autenticacao de dois fatores.")
        if request.installed_app:
            checklist.append("Desinstale o app remoto e execute analise de seguranca.")
        if request.shared_sms_code:
            checklist.append("Notifique prestador de servico e bloqueie acessos por SMS.")
        if not checklist:
            checklist.append("Nenhuma acao de risco confirmada. Monitore e informe familiares.")
        return RecoveryResponse(checklist=checklist)
