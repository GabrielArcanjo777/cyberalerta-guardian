package com.cyberalerta.companion.data.repository

import com.cyberalerta.companion.data.remote.AppResult
import com.cyberalerta.companion.data.remote.DeviceApi
import com.cyberalerta.companion.data.remote.apiCall
import com.cyberalerta.companion.data.remote.dto.AckEvent
import com.cyberalerta.companion.data.remote.dto.AckRequest
import com.cyberalerta.companion.data.remote.dto.AckResponse
import com.cyberalerta.companion.data.remote.dto.AlertDetailResponse

/** Alert detail fetch + ACK (Sprint 2, Unidade 4 — Secao 4.3 do plano). */
class AlertRepository(private val api: DeviceApi) {

    suspend fun getAlert(alertId: String): AppResult<AlertDetailResponse> = apiCall {
        api.getAlert(alertId)
    }

    suspend fun acknowledge(alertId: String, event: AckEvent): AppResult<AckResponse> = apiCall {
        api.acknowledgeAlert(alertId, AckRequest(event))
    }
}
