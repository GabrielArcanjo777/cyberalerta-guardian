package com.cyberalerta.companion.ui.alertdetail

import com.cyberalerta.companion.data.remote.AppResult
import com.cyberalerta.companion.data.remote.dto.AckEvent
import com.cyberalerta.companion.data.remote.dto.AckResponse
import com.cyberalerta.companion.data.remote.dto.AlertDetailResponse
import com.cyberalerta.companion.data.remote.dto.AlertState
import com.cyberalerta.companion.data.remote.dto.AlertType
import com.cyberalerta.companion.data.repository.AlertRepository
import com.cyberalerta.companion.util.MainDispatcherRule
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.mockk
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class AlertDetailViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private fun alert(state: AlertState) = AlertDetailResponse(
        alertId = "alrt-1",
        type = AlertType.TEST,
        severity = "INFO",
        protectedPersonAlias = "Dona Lucia",
        caseId = null,
        deepLink = "cyberalerta://case/alrt-1",
        state = state,
    )

    @Test
    fun `load auto-acknowledges opened when the alert only reached SENT`() = runTest {
        val repository = mockk<AlertRepository>()
        coEvery { repository.getAlert("alrt-1") } returns AppResult.Success(alert(AlertState.SENT))
        coEvery { repository.acknowledge("alrt-1", AckEvent.OPENED) } returns
            AppResult.Success(AckResponse(alertId = "alrt-1", state = AlertState.OPENED))

        val viewModel = AlertDetailViewModel(repository, "alrt-1")
        advanceUntilIdle()

        assertEquals(AlertState.OPENED, viewModel.uiState.value.alert?.state)
        coVerify { repository.acknowledge("alrt-1", AckEvent.OPENED) }
    }

    @Test
    fun `load does not re-acknowledge an alert that is already OPENED`() = runTest {
        val repository = mockk<AlertRepository>()
        coEvery { repository.getAlert("alrt-1") } returns AppResult.Success(alert(AlertState.OPENED))

        AlertDetailViewModel(repository, "alrt-1")
        advanceUntilIdle()

        coVerify(exactly = 0) { repository.acknowledge(any(), any()) }
    }

    @Test
    fun `load failure surfaces the error message and leaves alert null`() = runTest {
        val repository = mockk<AlertRepository>()
        coEvery { repository.getAlert("alrt-1") } returns
            AppResult.Error("Sem conexao com o servidor. Verifique a rede.")

        val viewModel = AlertDetailViewModel(repository, "alrt-1")
        advanceUntilIdle()

        assertEquals("Sem conexao com o servidor. Verifique a rede.", viewModel.uiState.value.errorMessage)
        assertEquals(null, viewModel.uiState.value.alert)
    }

    @Test
    fun `markActioned updates the alert state on success`() = runTest {
        val repository = mockk<AlertRepository>()
        coEvery { repository.getAlert("alrt-1") } returns AppResult.Success(alert(AlertState.OPENED))
        coEvery { repository.acknowledge("alrt-1", AckEvent.ACTIONED) } returns
            AppResult.Success(AckResponse(alertId = "alrt-1", state = AlertState.ACTIONED))

        val viewModel = AlertDetailViewModel(repository, "alrt-1")
        advanceUntilIdle()

        viewModel.markActioned()
        advanceUntilIdle()

        assertEquals(AlertState.ACTIONED, viewModel.uiState.value.alert?.state)
        assertEquals(false, viewModel.uiState.value.isSubmittingAction)
    }

    @Test
    fun `markActioned surfaces an error and keeps the previous state on failure`() = runTest {
        val repository = mockk<AlertRepository>()
        coEvery { repository.getAlert("alrt-1") } returns AppResult.Success(alert(AlertState.OPENED))
        coEvery { repository.acknowledge("alrt-1", AckEvent.ACTIONED) } returns
            AppResult.Error("Erro no servidor. Tente novamente em instantes.")

        val viewModel = AlertDetailViewModel(repository, "alrt-1")
        advanceUntilIdle()

        viewModel.markActioned()
        advanceUntilIdle()

        assertEquals("Erro no servidor. Tente novamente em instantes.", viewModel.uiState.value.errorMessage)
        assertEquals(AlertState.OPENED, viewModel.uiState.value.alert?.state)
    }
}
