package com.cyberalerta.companion.data.repository

import com.cyberalerta.companion.data.remote.AppResult
import com.cyberalerta.companion.data.remote.DeviceApi
import com.cyberalerta.companion.data.remote.apiCall
import com.cyberalerta.companion.data.remote.dto.DevicePlatform
import com.cyberalerta.companion.data.remote.dto.PairDeviceRequest
import com.cyberalerta.companion.data.remote.dto.PairDeviceResponse
import com.cyberalerta.companion.data.remote.dto.RegisterPushTokenRequest
import com.cyberalerta.companion.data.security.DeviceKeyProvider
import com.cyberalerta.companion.data.security.SecureSessionStore

/** Pairing + push-token registration (Sprint 2, Unidades 3/4). */
class DeviceRepository(
    private val api: DeviceApi,
    private val sessionStore: SecureSessionStore,
    private val deviceKeyProvider: DeviceKeyProvider,
) {

    val isPaired: Boolean
        get() = sessionStore.isPaired

    suspend fun pair(token: String): AppResult<PairDeviceResponse> = apiCall {
        val publicKey = deviceKeyProvider.getOrCreatePublicKeyBase64()
        val response = api.pairDevice(
            PairDeviceRequest(token = token.trim(), platform = DevicePlatform.ANDROID, publicKey = publicKey)
        )
        sessionStore.saveSession(deviceId = response.deviceId, sessionId = response.sessionId)
        response
    }

    suspend fun registerPushToken(fcmToken: String): AppResult<Unit> = apiCall {
        api.registerPushToken(RegisterPushTokenRequest(fcmToken))
        Unit
    }

    fun forgetLocalSession() = sessionStore.clear()
}
