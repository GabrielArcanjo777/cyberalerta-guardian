package com.cyberalerta.companion.ui.pairing

import com.cyberalerta.companion.data.remote.AppResult
import com.cyberalerta.companion.data.remote.dto.DeviceState
import com.cyberalerta.companion.data.remote.dto.PairDeviceResponse
import com.cyberalerta.companion.data.repository.DeviceRepository
import com.cyberalerta.companion.util.MainDispatcherRule
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.mockk
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test

class PairingViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private fun pairResponse() = PairDeviceResponse(
        deviceId = "device-1",
        sessionId = "session-1",
        state = DeviceState.PENDING_PAIRING,
    )

    @Test
    fun `pair with blank token shows an error without calling the repository`() = runTest {
        val deviceRepository = mockk<DeviceRepository>()
        val viewModel = PairingViewModel(deviceRepository, fetchFcmToken = { null })

        viewModel.onTokenChanged("   ")
        viewModel.pair()
        advanceUntilIdle()

        assertEquals("Cole o codigo do convite antes de continuar.", viewModel.uiState.value.errorMessage)
        coVerify(exactly = 0) { deviceRepository.pair(any()) }
    }

    @Test
    fun `successful pair registers the fcm token and emits paired`() = runTest {
        val deviceRepository = mockk<DeviceRepository>()
        coEvery { deviceRepository.pair("invite-token") } returns AppResult.Success(pairResponse())
        coEvery { deviceRepository.registerPushToken("fcm-token") } returns AppResult.Success(Unit)

        var pairedFired = false
        val viewModel = PairingViewModel(deviceRepository, fetchFcmToken = { "fcm-token" })
        // MutableSharedFlow has no replay — the collector must actually be
        // subscribed before pair() emits, or the event is lost. runCurrent()
        // lets this launch reach its collect() suspension point first.
        val collector = launch { viewModel.paired.collect { pairedFired = true } }
        runCurrent()

        viewModel.onTokenChanged("invite-token")
        viewModel.pair()
        advanceUntilIdle()

        assertTrue(pairedFired)
        assertFalse(viewModel.uiState.value.isLoading)
        assertNull(viewModel.uiState.value.errorMessage)
        coVerify { deviceRepository.registerPushToken("fcm-token") }
        collector.cancel()
    }

    @Test
    fun `pair still succeeds even when fcm token registration is unavailable`() = runTest {
        val deviceRepository = mockk<DeviceRepository>()
        coEvery { deviceRepository.pair("invite-token") } returns AppResult.Success(pairResponse())

        var pairedFired = false
        val viewModel = PairingViewModel(deviceRepository, fetchFcmToken = { null })
        val collector = launch { viewModel.paired.collect { pairedFired = true } }
        runCurrent()

        viewModel.onTokenChanged("invite-token")
        viewModel.pair()
        advanceUntilIdle()

        assertTrue(pairedFired)
        coVerify(exactly = 0) { deviceRepository.registerPushToken(any()) }
        collector.cancel()
    }

    @Test
    fun `failed pair surfaces the error and never touches push registration`() = runTest {
        val deviceRepository = mockk<DeviceRepository>()
        coEvery { deviceRepository.pair("bad-token") } returns
            AppResult.Error("Nao encontrado — pode ter expirado ou ja sido usado.")

        val viewModel = PairingViewModel(deviceRepository, fetchFcmToken = { "fcm-token" })
        viewModel.onTokenChanged("bad-token")
        viewModel.pair()
        advanceUntilIdle()

        assertEquals("Nao encontrado — pode ter expirado ou ja sido usado.", viewModel.uiState.value.errorMessage)
        assertFalse(viewModel.uiState.value.isLoading)
        coVerify(exactly = 0) { deviceRepository.registerPushToken(any()) }
    }

    @Test
    fun `prefillToken sets the token field without triggering pairing`() = runTest {
        val deviceRepository = mockk<DeviceRepository>()
        val viewModel = PairingViewModel(deviceRepository, fetchFcmToken = { null })

        viewModel.prefillToken("token-from-deep-link")

        assertEquals("token-from-deep-link", viewModel.uiState.value.token)
        coVerify(exactly = 0) { deviceRepository.pair(any()) }
    }
}
