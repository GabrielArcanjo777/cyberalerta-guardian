package com.cyberalerta.companion.ui.navigation

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import com.cyberalerta.companion.data.repository.AlertRepository
import com.cyberalerta.companion.data.repository.DeviceRepository
import com.cyberalerta.companion.ui.alertdetail.AlertDetailScreen
import com.cyberalerta.companion.ui.alertdetail.AlertDetailViewModel
import com.cyberalerta.companion.ui.alertdetail.AlertDetailViewModelFactory
import com.cyberalerta.companion.ui.home.HomeScreen
import com.cyberalerta.companion.ui.pairing.PairingScreen
import com.cyberalerta.companion.ui.pairing.PairingViewModel
import com.cyberalerta.companion.ui.pairing.PairingViewModelFactory

private const val ALERT_ID_ARG = "alertId"

@Composable
fun CyberAlertaNavHost(
    navController: NavHostController,
    deviceRepository: DeviceRepository,
    alertRepository: AlertRepository,
    pendingAlertId: String?,
    pendingPairingToken: String? = null,
) {
    val startDestination = if (deviceRepository.isPaired) Routes.HOME else Routes.PAIRING

    NavHost(navController = navController, startDestination = startDestination) {
        composable(Routes.PAIRING) {
            val viewModel: PairingViewModel = viewModel(factory = PairingViewModelFactory(deviceRepository))
            LaunchedEffect(pendingPairingToken) {
                pendingPairingToken?.let(viewModel::prefillToken)
            }
            PairingScreen(
                viewModel = viewModel,
                onPaired = {
                    navController.navigate(Routes.HOME) {
                        popUpTo(Routes.PAIRING) { inclusive = true }
                    }
                },
            )
        }
        composable(Routes.HOME) {
            HomeScreen(
                onForgetDevice = {
                    deviceRepository.forgetLocalSession()
                    navController.navigate(Routes.PAIRING) {
                        // Clears the whole back stack, including HOME —
                        // there is nothing to go "back" to once the local
                        // session is gone.
                        popUpTo(navController.graph.id) { inclusive = true }
                    }
                },
            )
        }
        composable(
            route = Routes.ALERT_DETAIL_PATTERN,
            arguments = listOf(navArgument(ALERT_ID_ARG) { type = NavType.StringType }),
        ) { backStackEntry ->
            val alertId = backStackEntry.arguments?.getString(ALERT_ID_ARG).orEmpty()
            val viewModel: AlertDetailViewModel = viewModel(
                key = alertId,
                factory = AlertDetailViewModelFactory(alertRepository, alertId),
            )
            AlertDetailScreen(viewModel = viewModel)
        }
    }

    // Cold start or singleTask re-entry via cyberalerta://case/{alertId}
    // (Secao 3.4/7.2). Ignored while unpaired — there is no session to
    // authenticate the detail fetch with yet.
    LaunchedEffect(pendingAlertId) {
        if (pendingAlertId != null && deviceRepository.isPaired) {
            navController.navigate(Routes.alertDetail(pendingAlertId))
        }
    }
}
