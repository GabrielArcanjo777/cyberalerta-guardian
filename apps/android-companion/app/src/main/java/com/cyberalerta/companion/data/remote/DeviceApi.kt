package com.cyberalerta.companion.data.remote

import com.cyberalerta.companion.data.remote.dto.AckRequest
import com.cyberalerta.companion.data.remote.dto.AckResponse
import com.cyberalerta.companion.data.remote.dto.AlertDetailResponse
import com.cyberalerta.companion.data.remote.dto.PairDeviceRequest
import com.cyberalerta.companion.data.remote.dto.PairDeviceResponse
import com.cyberalerta.companion.data.remote.dto.RegisterPushTokenRequest
import com.cyberalerta.companion.data.remote.dto.StatusResponse
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

/**
 * Only the device-facing surface of backend/app/devices + backend/app/notifications
 * (Sprint 2, Unidades 3/4/5). Admin-only routes (pairing-invitations, revoke,
 * test-push) belong to the Console/Windows side, not this app.
 *
 * pairDevice() is the one unauthenticated call — DeviceSessionInterceptor
 * attaches X-Device-Session to every other request once a session exists.
 */
interface DeviceApi {

    @POST("devices/pair")
    suspend fun pairDevice(@Body request: PairDeviceRequest): PairDeviceResponse

    @POST("devices/me/push-token")
    suspend fun registerPushToken(@Body request: RegisterPushTokenRequest): StatusResponse

    @GET("devices/me/alerts/{alertId}")
    suspend fun getAlert(@Path("alertId") alertId: String): AlertDetailResponse

    @POST("devices/me/alerts/{alertId}/ack")
    suspend fun acknowledgeAlert(
        @Path("alertId") alertId: String,
        @Body request: AckRequest,
    ): AckResponse
}
