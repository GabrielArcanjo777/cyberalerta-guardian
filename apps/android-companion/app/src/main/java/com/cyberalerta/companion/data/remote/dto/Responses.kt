package com.cyberalerta.companion.data.remote.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

// Mirrors backend/app/devices/schemas.py::PairDeviceResponse.
@Serializable
data class PairDeviceResponse(
    @SerialName("device_id") val deviceId: String,
    @SerialName("session_id") val sessionId: String,
    val state: DeviceState,
)

// Mirrors backend/app/devices/schemas.py::StatusResponse.
@Serializable
data class StatusResponse(val status: String)

// Mirrors backend/app/notifications/schemas.py::AlertDetailResponse.
// Timestamps stay as raw ISO-8601 strings — no kotlinx-datetime dependency
// for a handful of read-only display fields.
@Serializable
data class AlertDetailResponse(
    @SerialName("alert_id") val alertId: String,
    val type: AlertType,
    val severity: String,
    @SerialName("protected_person_alias") val protectedPersonAlias: String? = null,
    @SerialName("case_id") val caseId: String? = null,
    @SerialName("deep_link") val deepLink: String,
    val state: AlertState,
    @SerialName("sent_at") val sentAt: String? = null,
    @SerialName("delivered_at") val deliveredAt: String? = null,
    @SerialName("opened_at") val openedAt: String? = null,
    @SerialName("actioned_at") val actionedAt: String? = null,
)

// Mirrors backend/app/notifications/schemas.py::AckResponse.
@Serializable
data class AckResponse(
    @SerialName("alert_id") val alertId: String,
    val state: AlertState,
)
