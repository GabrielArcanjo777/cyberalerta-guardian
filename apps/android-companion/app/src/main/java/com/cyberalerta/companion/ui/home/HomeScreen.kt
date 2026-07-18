package com.cyberalerta.companion.ui.home

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp

/**
 * Deliberately minimal: the backend built in Sprint 2 exposes pairing, push
 * registration, single-alert fetch and ACK — there is no "list every alert
 * for this device" endpoint yet (that needs the real Case integration from
 * Sprint 5). This screen just confirms the device is paired and waiting;
 * BUILD_NOTES.md tracks the list endpoint as a known gap for a later sprint.
 */
@Composable
fun HomeScreen(onForgetDevice: () -> Unit) {
    Scaffold { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(24.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(
                text = "Aparelho pareado",
                style = MaterialTheme.typography.headlineSmall,
            )
            Spacer(Modifier.padding(top = 12.dp))
            Text(
                text = "Voce vai receber uma notificacao aqui sempre que o " +
                    "CyberAlerta Guardian identificar um risco na conversa " +
                    "monitorada. Nao e preciso manter o app aberto.",
                style = MaterialTheme.typography.bodyMedium,
                textAlign = TextAlign.Center,
            )
            Spacer(Modifier.padding(top = 32.dp))
            TextButton(onClick = onForgetDevice) {
                Text("Esquecer este pareamento")
            }
        }
    }
}
