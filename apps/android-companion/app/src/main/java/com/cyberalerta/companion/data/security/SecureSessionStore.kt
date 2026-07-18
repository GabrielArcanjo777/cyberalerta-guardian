package com.cyberalerta.companion.data.security

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

/**
 * Holds the device_id/session_id pair returned by POST /devices/pair — the
 * only credential this app has (Secao 6.2/6.3: no server secrets, no
 * message content, ever, on the client). Backed by AndroidX Security's
 * EncryptedSharedPreferences, whose own key lives in the Android Keystore.
 */
class SecureSessionStore(context: Context) {

    private val prefs: SharedPreferences by lazy {
        val masterKey = MasterKey.Builder(context.applicationContext)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()
        EncryptedSharedPreferences.create(
            context.applicationContext,
            PREFS_FILE_NAME,
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM,
        )
    }

    val isPaired: Boolean
        get() = getSessionId() != null

    fun getDeviceId(): String? = prefs.getString(KEY_DEVICE_ID, null)

    fun getSessionId(): String? = prefs.getString(KEY_SESSION_ID, null)

    fun saveSession(deviceId: String, sessionId: String) {
        prefs.edit()
            .putString(KEY_DEVICE_ID, deviceId)
            .putString(KEY_SESSION_ID, sessionId)
            .apply()
    }

    /** Local-only sign-out — does not call the backend. Revocation
     * (backend/app/devices/service.py::revoke_device) is the operator's
     * action; this just forgets the credential on this device. */
    fun clear() {
        prefs.edit().clear().apply()
    }

    private companion object {
        const val PREFS_FILE_NAME = "cyberalerta_secure_session"
        const val KEY_DEVICE_ID = "device_id"
        const val KEY_SESSION_ID = "session_id"
    }
}
