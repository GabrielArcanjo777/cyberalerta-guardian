package com.cyberalerta.companion.ui.pairing

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.cyberalerta.companion.data.remote.AppResult
import com.cyberalerta.companion.data.repository.DeviceRepository
import com.cyberalerta.companion.push.fetchCurrentFcmToken
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class PairingUiState(
    val token: String = "",
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
)

/**
 * Secao 6.2 do plano: cola/recebe o token de uso unico, gera prova de posse
 * (DeviceKeyProvider, dentro de DeviceRepository.pair) e troca por uma
 * sessao de device.
 *
 * fetchFcmToken is injected (defaults to the real Firebase call via the
 * factory below) instead of called directly, so this ViewModel is testable
 * on the plain JVM without Robolectric/instrumentation — FirebaseMessaging
 * .getInstance() requires a real Android environment.
 */
class PairingViewModel(
    private val deviceRepository: DeviceRepository,
    private val fetchFcmToken: suspend () -> String? = ::fetchCurrentFcmToken,
) : ViewModel() {

    private val _uiState = MutableStateFlow(PairingUiState())
    val uiState: StateFlow<PairingUiState> = _uiState.asStateFlow()

    private val _paired = MutableSharedFlow<Unit>()
    val paired: SharedFlow<Unit> = _paired.asSharedFlow()

    fun prefillToken(token: String) {
        _uiState.update { it.copy(token = token) }
    }

    fun onTokenChanged(value: String) {
        _uiState.update { it.copy(token = value, errorMessage = null) }
    }

    fun pair() {
        val token = _uiState.value.token.trim()
        if (token.isEmpty()) {
            _uiState.update { it.copy(errorMessage = "Cole o codigo do convite antes de continuar.") }
            return
        }
        if (_uiState.value.isLoading) return

        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            when (val result = deviceRepository.pair(token)) {
                is AppResult.Success -> {
                    _uiState.update { it.copy(isLoading = false) }
                    // Best-effort: pairing already succeeded regardless of
                    // whether this registers cleanly. onNewToken() in
                    // CyberAlertaFirebaseMessagingService covers rotation/
                    // retry later if this call fails right now.
                    fetchFcmToken()?.let { fcmToken -> deviceRepository.registerPushToken(fcmToken) }
                    _paired.emit(Unit)
                }
                is AppResult.Error -> {
                    _uiState.update { it.copy(isLoading = false, errorMessage = result.message) }
                }
            }
        }
    }
}

class PairingViewModelFactory(private val deviceRepository: DeviceRepository) : ViewModelProvider.Factory {
    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        require(modelClass.isAssignableFrom(PairingViewModel::class.java))
        return PairingViewModel(deviceRepository) as T
    }
}
