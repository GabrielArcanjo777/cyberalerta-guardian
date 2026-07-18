package com.cyberalerta.companion.data.repository

import com.cyberalerta.companion.data.remote.AppResult
import com.cyberalerta.companion.data.remote.DeviceApi
import com.cyberalerta.companion.data.remote.dto.AckEvent
import com.cyberalerta.companion.data.remote.dto.AckResponse
import com.cyberalerta.companion.data.remote.dto.AlertDetailResponse
import com.cyberalerta.companion.data.remote.dto.AlertState
import com.cyberalerta.companion.data.remote.dto.AlertType
import io.mockk.coEvery
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.ResponseBody.Companion.toResponseBody
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import retrofit2.HttpException
import retrofit2.Response

class AlertRepositoryTest {

    private fun sampleAlert(state: AlertState = AlertState.SENT) = AlertDetailResponse(
        alertId = "alrt-1",
        type = AlertType.TEST,
        severity = "INFO",
        protectedPersonAlias = null,
        caseId = null,
        deepLink = "cyberalerta://case/alrt-1",
        state = state,
    )

    @Test
    fun `getAlert returns Success with the API response`() = runTest {
        val api = mockk<DeviceApi>()
        coEvery { api.getAlert("alrt-1") } returns sampleAlert()
        val repository = AlertRepository(api)

        val result = repository.getAlert("alrt-1")

        assertTrue(result is AppResult.Success)
        assertEquals("alrt-1", (result as AppResult.Success).data.alertId)
    }

    @Test
    fun `getAlert maps a 404 to a not-found message`() = runTest {
        val api = mockk<DeviceApi>()
        val notFound = HttpException(
            Response.error<AlertDetailResponse>(404, "{}".toResponseBody("application/json".toMediaType()))
        )
        coEvery { api.getAlert("missing") } throws notFound
        val repository = AlertRepository(api)

        val result = repository.getAlert("missing")

        assertTrue(result is AppResult.Error)
        assertTrue((result as AppResult.Error).message.contains("Nao encontrado"))
    }

    @Test
    fun `acknowledge forwards the event and returns the resulting state`() = runTest {
        val api = mockk<DeviceApi>()
        coEvery { api.acknowledgeAlert("alrt-1", any()) } returns
            AckResponse(alertId = "alrt-1", state = AlertState.OPENED)
        val repository = AlertRepository(api)

        val result = repository.acknowledge("alrt-1", AckEvent.OPENED)

        assertTrue(result is AppResult.Success)
        assertEquals(AlertState.OPENED, (result as AppResult.Success).data.state)
    }
}
