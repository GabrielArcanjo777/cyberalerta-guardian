package com.cyberalerta.companion.ui.alertdetail

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.cyberalerta.companion.data.remote.AppResult
import com.cyberalerta.companion.data.remote.dto.AckEvent
import com.cyberalerta.companion.data.remote.dto.AlertDetailResponse
import com.cyberalerta.companion.data.remote.dto.AlertState
import com.cyberalerta.companion.data.repository.AlertRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class AlertDetailUiState(
    val isLoading: Boolean = true,
    val alert: AlertDetailResponse? = null,
    val errorMessage: String? = null,
    val isSubmittingAction: Boolean = false,
)

/**
 * Secao 4.3/6.2 do plano: ao abrir o caso, o app autentica o dispositivo,
 * busca os detalhes e envia ACK. Neste sprint o "caso" e sempre um alerta
 * TEST sintetico (POST /devices/{id}/test-push) — nao ha Case real nem
 * numero de telefone para ligar ainda (isso e integracao com o Case de
 * verdade, Sprint 5), entao a unica acao disponivel aqui e confirmar que o
 * alerta foi tratado.
 */
class AlertDetailViewModel(
    private val alertRepository: AlertRepository,
    private val alertId: String,
) : ViewModel() {

    private val _uiState = MutableStateFlow(AlertDetailUiState())
    val uiState: StateFlow<AlertDetailUiState> = _uiState.asStateFlow()

    init {
        load()
    }

    fun load() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            when (val result = alertRepository.getAlert(alertId)) {
                is AppResult.Success -> {
                    _uiState.update { it.copy(isLoading = false, alert = result.data) }
                    acknowledgeOpenedIfNeeded(result.data)
                }
                is AppResult.Error -> _uiState.update { it.copy(isLoading = false, errorMessage = result.message) }
            }
        }
    }

    /** Auto-ACK "opened" as soon as the detail loads — this is what "abrir
     * o caso" means server-side, and for a PENDING_PAIRING device it is
     * exactly the confirmation that flips the device to ACTIVE. Best-effort:
     * a failed ACK here does not block the screen, the user can still see
     * the alert and retry via markActioned(). */
    private suspend fun acknowledgeOpenedIfNeeded(alert: AlertDetailResponse) {
        if (alert.state != AlertState.SENT && alert.state != AlertState.DELIVERED) return
        when (val result = alertRepository.acknowledge(alertId, AckEvent.OPENED)) {
            is AppResult.Success -> _uiState.update { current ->
                current.copy(alert = current.alert?.copy(state = result.data.state))
            }
            is AppResult.Error -> Unit
        }
    }

    fun markActioned() {
        if (_uiState.value.isSubmittingAction) return
        viewModelScope.launch {
            _uiState.update { it.copy(isSubmittingAction = true, errorMessage = null) }
            when (val result = alertRepository.acknowledge(alertId, AckEvent.ACTIONED)) {
                is AppResult.Success -> _uiState.update { current ->
                    current.copy(
                        isSubmittingAction = false,
                        alert = current.alert?.copy(state = result.data.state),
                    )
                }
                is AppResult.Error -> _uiState.update {
                    it.copy(isSubmittingAction = false, errorMessage = result.message)
                }
            }
        }
    }
}

class AlertDetailViewModelFactory(
    private val alertRepository: AlertRepository,
    private val alertId: String,
) : ViewModelProvider.Factory {
    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        require(modelClass.isAssignableFrom(AlertDetailViewModel::class.java))
        return AlertDetailViewModel(alertRepository, alertId) as T
    }
}
