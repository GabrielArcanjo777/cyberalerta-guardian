package com.cyberalerta.companion.ui.navigation

object Routes {
    const val PAIRING = "pairing"
    const val HOME = "home"
    const val ALERT_DETAIL_PATTERN = "alert/{alertId}"

    fun alertDetail(alertId: String) = "alert/$alertId"
}
