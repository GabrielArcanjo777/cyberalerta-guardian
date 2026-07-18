package com.cyberalerta.companion.data.remote

import com.cyberalerta.companion.data.security.SecureSessionStore
import okhttp3.Interceptor
import okhttp3.Response

/** Same header name as backend/app/devices/device_auth.py::DEVICE_SESSION_HEADER. */
private const val DEVICE_SESSION_HEADER = "X-Device-Session"

/**
 * Attaches the bearer session (Secao 6.2/Unidade 4) to every request once
 * pairing has produced one. Harmless no-op before pairing — POST
 * /devices/pair does not require it and ignores extra headers.
 */
class DeviceSessionInterceptor(private val sessionStore: SecureSessionStore) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val sessionId = sessionStore.getSessionId()
        val original = chain.request()
        val request = if (sessionId == null) {
            original
        } else {
            original.newBuilder().addHeader(DEVICE_SESSION_HEADER, sessionId).build()
        }
        return chain.proceed(request)
    }
}
