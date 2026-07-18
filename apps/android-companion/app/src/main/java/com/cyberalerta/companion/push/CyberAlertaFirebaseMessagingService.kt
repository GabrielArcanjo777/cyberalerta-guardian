package com.cyberalerta.companion.push

import com.cyberalerta.companion.CyberAlertaApplication
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch

/**
 * Sprint 2 Unidade 4 / Sprint 3: receives the CASE_ALERT/TEST push (Secao
 * 7.2) as an FCM *data* message (no "notification" block server-side, so
 * this callback always fires, even in the background) and turns it into a
 * local notification. Tapping it opens MainActivity via the deep link,
 * which routes to AlertDetailScreen and fires the "opened" ACK there.
 */
class CyberAlertaFirebaseMessagingService : FirebaseMessagingService() {

    private val serviceScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    override fun onNewToken(token: String) {
        super.onNewToken(token)
        val app = application as CyberAlertaApplication
        if (!app.sessionStore.isPaired) return
        serviceScope.launch { app.deviceRepository.registerPushToken(token) }
    }

    override fun onMessageReceived(message: RemoteMessage) {
        super.onMessageReceived(message)
        val data = message.data
        val alertId = data["alert_id"] ?: return
        NotificationHelper.showAlertNotification(
            context = applicationContext,
            alertId = alertId,
            severity = data["severity"],
            protectedPersonAlias = data["protected_person_alias"],
            deepLink = data["deep_link"],
        )
    }

    override fun onDestroy() {
        super.onDestroy()
        serviceScope.cancel()
    }
}
