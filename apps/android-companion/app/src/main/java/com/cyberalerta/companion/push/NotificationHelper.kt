package com.cyberalerta.companion.push

import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.net.toUri
import com.cyberalerta.companion.MainActivity
import com.cyberalerta.companion.R

object NotificationHelper {

    /** Secao 7.2 do plano: o payload de push e minimo (alert_id/severity/
     * alias/deep_link), entao e tudo que esta notificacao pode mostrar —
     * nenhum conteudo de mensagem chega ate aqui, por desenho. */
    fun showAlertNotification(
        context: Context,
        alertId: String,
        severity: String?,
        protectedPersonAlias: String?,
        deepLink: String?,
    ) {
        val targetUri = (deepLink ?: "cyberalerta://case/$alertId").toUri()
        val intent = Intent(Intent.ACTION_VIEW, targetUri, context, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            context,
            alertId.hashCode(),
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )

        val isHighSeverity = severity?.uppercase() in setOf("CRITICAL", "HIGH")
        val title = if (isHighSeverity) "Alerta de risco" else "CyberAlerta Guardian"
        val text = protectedPersonAlias?.let { "Verifique o caso de $it agora." }
            ?: "Toque para ver os detalhes."

        val notification = NotificationCompat.Builder(context, context.getString(R.string.notification_channel_id))
            // Placeholder system glyph — swap for a real branded vector
            // asset once the mobile design system exists.
            .setSmallIcon(android.R.drawable.ic_dialog_alert)
            .setContentTitle(title)
            .setContentText(text)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .build()

        runCatching {
            NotificationManagerCompat.from(context).notify(alertId.hashCode(), notification)
        }
        // A denied POST_NOTIFICATIONS permission throws SecurityException on
        // some OEM builds even after the checks in MainActivity — the user
        // can still open the app manually, so this stays silent rather than
        // crashing the FCM service.
    }
}
