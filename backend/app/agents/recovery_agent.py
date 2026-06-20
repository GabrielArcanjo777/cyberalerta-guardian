from app.schemas.recovery import RecoveryRequest, RecoveryResponse


class RecoveryAgent:
    def analyze(self, request: RecoveryRequest) -> RecoveryResponse:
        checklist = []
        immediate_steps = []

        if request.paid or request.already_paid:
            checklist.append("Contactar instituicao financeira imediatamente.")
            checklist.append("Registrar ocorrencia de fraude e bloquear transacao.")
            immediate_steps.append("Ligar para o banco e solicitar bloqueio da transferencia.")
            immediate_steps.append("Registrar boletim de ocorrencia.")

        if request.clicked_link or request.has_clicked_link:
            checklist.append("Nao acesse o link novamente e verifique se ha malware.")
            immediate_steps.append("Rodar antivirus no dispositivo.")
            immediate_steps.append("Alterar senhas de contas principais.")

        if request.shared_documents:
            checklist.append("Verificar se documentos enviados podem ter sido usados indevidamente.")
            immediate_steps.append("Monitorar contas e servicos em nome do titular.")

        if request.shared_password or request.has_shared_password:
            checklist.append("Altere senhas e ative autenticacao de dois fatores.")
            immediate_steps.append("Trocar senhas de email, banco e redes sociais.")
            immediate_steps.append("Ativar 2FA em todas as contas possiveis.")

        if request.installed_app or request.has_installed_remote_app:
            checklist.append("Desinstale o app remoto e execute analise de seguranca.")
            immediate_steps.append("Desinstalar aplicativos desconhecidos.")
            immediate_steps.append("Reiniciar o dispositivo em modo seguro.")

        if request.shared_sms_code or request.has_sent_code:
            checklist.append("Notifique prestador de servico e bloqueie acessos por SMS.")
            immediate_steps.append("Contatar operadora e servicos afetados.")
            immediate_steps.append("Solicitar novo chip se necessario.")

        if not checklist:
            checklist.append("Nenhuma acao de risco confirmada. Monitore e informe familiares.")
            immediate_steps.append("Manter atencao e comunicar a familia sobre a situacao.")

        summary = self._build_summary(request)
        whatsapp_summary = self._build_whatsapp_summary(request, immediate_steps)

        return RecoveryResponse(
            checklist=checklist,
            incident_type=request.incident_type or self._infer_incident_type(request),
            summary=summary,
            whatsapp_summary_message=whatsapp_summary,
            immediate_steps=immediate_steps if immediate_steps else checklist[:3],
            disclaimer=(
                "O CyberAlerta Guardian nao substitui banco, policia, advogado ou canais oficiais. "
                "Procure ajuda profissional para orientacao completa."
            ),
            n8n_action="start_recovery",
            case_id=request.case_id,
        )

    def _build_summary(self, request: RecoveryRequest) -> str:
        parts = []
        if request.paid or request.already_paid:
            parts.append("Pagamento ja realizado.")
        if request.clicked_link or request.has_clicked_link:
            parts.append("Link suspeito clicado.")
        if request.shared_password or request.has_shared_password:
            parts.append("Senha compartilhada.")
        if request.installed_app or request.has_installed_remote_app:
            parts.append("App remoto instalado.")
        if request.shared_sms_code or request.has_sent_code:
            parts.append("Codigo SMS compartilhado.")
        if not parts:
            parts.append("Incidente reportado sem acoes de risco confirmadas.")
        return " ".join(parts)

    def _build_whatsapp_summary(self, request: RecoveryRequest, steps: list[str]) -> str:
        header = "Recuperacao CyberAlerta Guardian\n\n"
        if steps:
            header += "Passos imediatos:\n" + "\n".join(f"- {s}" for s in steps[:5]) + "\n\n"
        header += (
            "Lembre-se: o Guardian ajuda com orientacao inicial, "
            "mas nao substitui o contato direto com banco, policia ou orgaos oficiais."
        )
        return header

    def _infer_incident_type(self, request: RecoveryRequest) -> str:
        if request.paid or request.already_paid:
            return "pix_sent"
        if request.clicked_link or request.has_clicked_link:
            return "link_clicked"
        if request.shared_password or request.has_shared_password:
            return "password_shared"
        if request.installed_app or request.has_installed_remote_app:
            return "app_installed"
        if request.shared_sms_code or request.has_sent_code:
            return "code_shared"
        return "generic_incident"
