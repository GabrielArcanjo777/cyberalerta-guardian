package com.cyberalerta.companion

import android.app.Application
import android.app.NotificationChannel
import android.app.NotificationManager
import android.os.Build
import com.cyberalerta.companion.data.remote.ApiClient
import com.cyberalerta.companion.data.remote.DeviceApi
import com.cyberalerta.companion.data.repository.AlertRepository
import com.cyberalerta.companion.data.repository.DeviceRepository
import com.cyberalerta.companion.data.security.DeviceKeyProvider
import com.cyberalerta.companion.data.security.SecureSessionStore

/**
 * No DI framework here on purpose — the object graph is small enough that
 * Hilt/Koin would add build-time risk (annotation processing, another
 * plugin) without buying much. Everything is a lazily-built singleton
 * exposed through this Application instance instead.
 */
class CyberAlertaApplication : Application() {

    lateinit var sessionStore: SecureSessionStore
        private set
    lateinit var deviceKeyProvider: DeviceKeyProvider
        private set
    lateinit var deviceRepository: DeviceRepository
        private set
    lateinit var alertRepository: AlertRepository
        private set

    override fun onCreate() {
        super.onCreate()
        sessionStore = SecureSessionStore(this)
        deviceKeyProvider = DeviceKeyProvider()
        val api: DeviceApi = ApiClient.create(baseUrl = BuildConfig.API_BASE_URL, sessionStore = sessionStore)
        deviceRepository = DeviceRepository(
            api = api,
            sessionStore = sessionStore,
            deviceKeyProvider = deviceKeyProvider,
        )
        alertRepository = AlertRepository(api = api)
        createNotificationChannel()
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return
        val channel = NotificationChannel(
            getString(R.string.notification_channel_id),
            getString(R.string.notification_channel_name),
            NotificationManager.IMPORTANCE_HIGH,
        ).apply {
            description = getString(R.string.notification_channel_description)
        }
        getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
    }
}
