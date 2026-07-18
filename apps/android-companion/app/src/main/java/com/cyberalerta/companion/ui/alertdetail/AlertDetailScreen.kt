package com.cyberalerta.companion.ui.alertdetail

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.cyberalerta.companion.data.remote.dto.AlertState

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AlertDetailScreen(viewModel: AlertDetailViewModel) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = { TopAppBar(title = { Text("Alerta") }) },
    ) { padding ->
        Column(modifier = Modifier.fillMaxSize().padding(padding).padding(24.dp)) {
            when {
                uiState.isLoading -> LoadingState()
                uiState.alert == null -> ErrorState(
                    message = uiState.errorMessage ?: "Nao foi possivel carregar este alerta.",
                    onRetry = viewModel::load,
                )
                else -> AlertContent(
                    severity = uiState.alert!!.severity,
                    protectedPersonAlias = uiState.alert!!.protectedPersonAlias,
                    state = uiState.alert!!.state,
                    isSubmittingAction = uiState.isSubmittingAction,
                    errorMessage = uiState.errorMessage,
                    onMarkActioned = viewModel::markActioned,
                )
            }
        }
    }
}

@Composable
private fun LoadingState() {
    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        CircularProgressIndicator()
    }
}

@Composable
private fun ErrorState(message: String, onRetry: () -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(text = message, style = MaterialTheme.typography.bodyLarge)
        Spacer(Modifier.padding(top = 16.dp))
        Button(onClick = onRetry) { Text("Tentar novamente") }
    }
}

@Composable
private fun AlertContent(
    severity: String,
    protectedPersonAlias: String?,
    state: AlertState,
    isSubmittingAction: Boolean,
    errorMessage: String?,
    onMarkActioned: () -> Unit,
) {
    Text(text = "Severidade: $severity", style = MaterialTheme.typography.titleLarge)
    Spacer(Modifier.padding(top = 8.dp))
    Text(
        text = protectedPersonAlias?.let { "Pessoa protegida: $it" }
            ?: "Alerta de teste — nenhuma pessoa protegida vinculada.",
        style = MaterialTheme.typography.bodyLarge,
    )
    Spacer(Modifier.padding(top = 8.dp))
    Text(text = "Status: ${state.displayLabel()}", style = MaterialTheme.typography.bodyMedium)

    errorMessage?.let { message ->
        Spacer(Modifier.padding(top = 16.dp))
        Text(text = message, color = MaterialTheme.colorScheme.error)
    }

    Spacer(Modifier.padding(top = 32.dp))
    Row(modifier = Modifier.fillMaxWidth()) {
        Button(
            onClick = onMarkActioned,
            enabled = !isSubmittingAction && state != AlertState.ACTIONED,
            modifier = Modifier.fillMaxWidth(),
        ) {
            if (isSubmittingAction) {
                CircularProgressIndicator(
                    modifier = Modifier.padding(vertical = 2.dp),
                    color = MaterialTheme.colorScheme.onPrimary,
                )
            } else {
                Text(if (state == AlertState.ACTIONED) "Ja marcado como tratado" else "Marcar como tratado")
            }
        }
    }
}

private fun AlertState.displayLabel(): String = when (this) {
    AlertState.PENDING -> "pendente"
    AlertState.SENT -> "enviado"
    AlertState.DELIVERED -> "entregue"
    AlertState.OPENED -> "aberto"
    AlertState.ACTIONED -> "tratado"
    AlertState.FAILED -> "falhou"
    AlertState.EXPIRED -> "expirado"
}
