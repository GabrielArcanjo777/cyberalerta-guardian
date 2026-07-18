package com.cyberalerta.companion

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.core.content.ContextCompat
import androidx.navigation.compose.rememberNavController
import com.cyberalerta.companion.ui.navigation.CyberAlertaNavHost
import com.cyberalerta.companion.ui.theme.CyberAlertaCompanionTheme

class MainActivity : ComponentActivity() {

    private var pendingAlertId by mutableStateOf<String?>(null)
    private var pendingPairingToken by mutableStateOf<String?>(null)

    private val requestNotificationPermission = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { /* denial just means no heads-up notification; the app still works when opened manually */ }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        requestNotificationPermissionIfNeeded()
        consumeIntent(intent)

        val app = application as CyberAlertaApplication
        setContent {
            CyberAlertaCompanionTheme {
                val navController = rememberNavController()
                CyberAlertaNavHost(
                    navController = navController,
                    deviceRepository = app.deviceRepository,
                    alertRepository = app.alertRepository,
                    pendingAlertId = pendingAlertId,
                    pendingPairingToken = pendingPairingToken,
                )
            }
        }
    }

    // launchMode="singleTask" (manifest) means a second deep-link tap while
    // the app is already running arrives here instead of a fresh onCreate.
    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        consumeIntent(intent)
    }

    private fun consumeIntent(intent: Intent?) {
        val uri = intent?.data ?: return
        when (uri.host) {
            "case" -> pendingAlertId = uri.firstPathSegmentOrNull()
            "pair" -> pendingPairingToken = uri.getQueryParameter("token")
        }
    }

    private fun requestNotificationPermissionIfNeeded() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU) return
        val granted = ContextCompat.checkSelfPermission(
            this, Manifest.permission.POST_NOTIFICATIONS
        ) == PackageManager.PERMISSION_GRANTED
        if (!granted) {
            requestNotificationPermission.launch(Manifest.permission.POST_NOTIFICATIONS)
        }
    }
}

private fun Uri.firstPathSegmentOrNull(): String? = pathSegments.firstOrNull()
