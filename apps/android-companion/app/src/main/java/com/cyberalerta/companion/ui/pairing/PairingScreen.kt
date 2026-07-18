package com.cyberalerta.companion.ui.pairing

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun PairingScreen(
    viewModel: PairingViewModel,
    onPaired: () -> Unit,
) {
    val uiState by viewModel.uiState.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.paired.collect { onPaired() }
    }

    Scaffold { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(24.dp),
            verticalArrangement = Arrangement.Center,
        ) {
            Text(
                text = "Parear este aparelho",
                style = MaterialTheme.typography.headlineSmall,
            )
            Spacer(Modifier.padding(top = 8.dp))
            Text(
                text = "Cole abaixo o codigo de convite gerado pelo administrador " +
                    "no Console (validade curta, uso unico). Se voce escaneou um QR " +
                    "com a camera do aparelho, o codigo pode ja estar preenchido.",
                style = MaterialTheme.typography.bodyMedium,
            )
            Spacer(Modifier.padding(top = 24.dp))
            OutlinedTextField(
                value = uiState.token,
                onValueChange = viewModel::onTokenChanged,
                label = { Text("Codigo do convite") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
                enabled = !uiState.isLoading,
            )
            uiState.errorMessage?.let { message ->
                Spacer(Modifier.padding(top = 8.dp))
                Text(text = message, color = MaterialTheme.colorScheme.error)
            }
            Spacer(Modifier.padding(top = 24.dp))
            Button(
                onClick = viewModel::pair,
                enabled = !uiState.isLoading,
                modifier = Modifier.fillMaxWidth(),
            ) {
                if (uiState.isLoading) {
                    CircularProgressIndicator(
                        modifier = Modifier.padding(vertical = 2.dp),
                        color = MaterialTheme.colorScheme.onPrimary,
                    )
                } else {
                    Text("Parear")
                }
            }
        }
    }
}
