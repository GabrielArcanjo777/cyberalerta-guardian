package com.cyberalerta.companion.data.remote

import com.cyberalerta.companion.BuildConfig
import com.cyberalerta.companion.data.security.SecureSessionStore
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.kotlinx.serialization.asConverterFactory
import retrofit2.create

object ApiClient {

    private val json = Json {
        ignoreUnknownKeys = true
        explicitNulls = false
    }

    fun create(baseUrl: String, sessionStore: SecureSessionStore): DeviceApi {
        val logging = HttpLoggingInterceptor().apply {
            // Body-level logging only in debug builds — never in a build a
            // user could sideload/inspect, and the payload is push-minimal
            // anyway (Secao 7.2), so there is no message content to leak.
            level = if (BuildConfig.DEBUG) {
                HttpLoggingInterceptor.Level.BODY
            } else {
                HttpLoggingInterceptor.Level.NONE
            }
        }
        val client = OkHttpClient.Builder()
            .addInterceptor(DeviceSessionInterceptor(sessionStore))
            .addInterceptor(logging)
            .build()

        return Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(client)
            .addConverterFactory(json.asConverterFactory("application/json".toMediaType()))
            .build()
            .create()
    }
}
