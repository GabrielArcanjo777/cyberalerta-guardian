package com.cyberalerta.companion.data.remote.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

// Mirrors backend/app/devices/schemas.py::PairDeviceRequest.
@Serializable
data class PairDeviceRequest(
    val token: String,
    val platform: DevicePlatform,
    @SerialName("public_key") val publicKey: String,
)

// Mirrors backend/app/devices/schemas.py::RegisterPushTokenRequest.
@Serializable
data class RegisterPushTokenRequest(val token: String)

// Mirrors backend/app/notifications/schemas.py::AckRequest.
@Serializable
data class AckRequest(val event: AckEvent)
