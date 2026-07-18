package com.cyberalerta.companion.data.repository

import com.cyberalerta.companion.data.remote.AppResult
import com.cyberalerta.companion.data.remote.DeviceApi
import com.cyberalerta.companion.data.remote.dto.DevicePlatform
import com.cyberalerta.companion.data.remote.dto.DeviceState
import com.cyberalerta.companion.data.remote.dto.PairDeviceResponse
import com.cyberalerta.companion.data.remote.dto.StatusResponse
import com.cyberalerta.companion.data.security.DeviceKeyProvider
import com.cyberalerta.companion.data.security.SecureSessionStore
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import java.io.IOException
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertTrue
import org.junit.Test

class DeviceRepositoryTest {

    private fun pairResponse() = PairDeviceResponse(
        deviceId = "device-1",
        sessionId = "session-1",
        state = DeviceState.PENDING_PAIRING,
    )

    @Test
    fun `pair sends the proof-of-possession public key and saves the returned session`() = runTest {
        val api = mockk<DeviceApi>()
        val sessionStore = mockk<SecureSessionStore>(relaxed = true)
        val keyProvider = mockk<DeviceKeyProvider>()
        every { keyProvider.getOrCreatePublicKeyBase64() } returns "pubkey-b64"
        coEvery {
            api.pairDevice(match { it.publicKey == "pubkey-b64" && it.platform == DevicePlatform.ANDROID })
        } returns pairResponse()

        val repository = DeviceRepository(api, sessionStore, keyProvider)
        val result = repository.pair("invite-token")

        assertTrue(result is AppResult.Success)
        verify { sessionStore.saveSession(deviceId = "device-1", sessionId = "session-1") }
    }

    @Test
    fun `pair trims the pasted token before sending it`() = runTest {
        val api = mockk<DeviceApi>()
        val sessionStore = mockk<SecureSessionStore>(relaxed = true)
        val keyProvider = mockk<DeviceKeyProvider>()
        every { keyProvider.getOrCreatePublicKeyBase64() } returns "pubkey-b64"
        coEvery { api.pairDevice(any()) } returns pairResponse()

        val repository = DeviceRepository(api, sessionStore, keyProvider)
        repository.pair("  invite-token  ")

        coVerify { api.pairDevice(match { it.token == "invite-token" }) }
    }

    @Test
    fun `pair failure does not save any session`() = runTest {
        val api = mockk<DeviceApi>()
        val sessionStore = mockk<SecureSessionStore>(relaxed = true)
        val keyProvider = mockk<DeviceKeyProvider>()
        every { keyProvider.getOrCreatePublicKeyBase64() } returns "pubkey-b64"
        coEvery { api.pairDevice(any()) } throws IOException("no network")

        val repository = DeviceRepository(api, sessionStore, keyProvider)
        val result = repository.pair("invite-token")

        assertTrue(result is AppResult.Error)
        verify(exactly = 0) { sessionStore.saveSession(any(), any()) }
    }

    @Test
    fun `registerPushToken forwards the fcm token`() = runTest {
        val api = mockk<DeviceApi>()
        val sessionStore = mockk<SecureSessionStore>(relaxed = true)
        val keyProvider = mockk<DeviceKeyProvider>()
        coEvery { api.registerPushToken(any()) } returns StatusResponse(status = "ok")

        val repository = DeviceRepository(api, sessionStore, keyProvider)
        val result = repository.registerPushToken("fcm-token-xyz")

        assertTrue(result is AppResult.Success)
        coVerify { api.registerPushToken(match { it.token == "fcm-token-xyz" }) }
    }
}
