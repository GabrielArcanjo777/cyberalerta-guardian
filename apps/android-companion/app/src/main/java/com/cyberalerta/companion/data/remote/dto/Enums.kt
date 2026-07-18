package com.cyberalerta.companion.data.remote.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

// Mirrors backend/app/devices/models.py::DevicePlatform.
@Serializable
enum class DevicePlatform {
    @SerialName("android") ANDROID,
    @SerialName("windows") WINDOWS,
    @SerialName("web") WEB,
}

// Mirrors backend/app/devices/models.py::DeviceState (Plano Mestre Secao 4.5).
@Serializable
enum class DeviceState {
    @SerialName("pending_pairing") PENDING_PAIRING,
    @SerialName("active") ACTIVE,
    @SerialName("revoked") REVOKED,
    @SerialName("lost") LOST,
    @SerialName("expired") EXPIRED,
}

// Mirrors backend/app/notifications/models.py::AlertType.
@Serializable
enum class AlertType {
    @SerialName("test") TEST,
    @SerialName("case_alert") CASE_ALERT,
}

// Mirrors backend/app/notifications/models.py::AlertState (Plano Mestre Secao 4.5).
@Serializable
enum class AlertState {
    @SerialName("pending") PENDING,
    @SerialName("sent") SENT,
    @SerialName("delivered") DELIVERED,
    @SerialName("opened") OPENED,
    @SerialName("actioned") ACTIONED,
    @SerialName("failed") FAILED,
    @SerialName("expired") EXPIRED,
}

// Mirrors backend/app/notifications/models.py::AckEvent.
@Serializable
enum class AckEvent {
    @SerialName("delivered") DELIVERED,
    @SerialName("opened") OPENED,
    @SerialName("actioned") ACTIONED,
}
