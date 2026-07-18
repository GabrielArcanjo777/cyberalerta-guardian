package com.cyberalerta.companion.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

private val DarkColors = darkColorScheme(
    primary = BrandPrimary,
    onPrimary = BrandOnPrimary,
    background = BrandBackground,
    surface = BrandSurface,
    onSurface = BrandOnSurface,
    error = BrandCritical,
)

private val LightColors = lightColorScheme(
    primary = BrandPrimaryDark,
    onPrimary = BrandOnPrimary,
    error = BrandCritical,
)

@Composable
fun CyberAlertaCompanionTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit,
) {
    val colorScheme = if (darkTheme) DarkColors else LightColors
    MaterialTheme(
        colorScheme = colorScheme,
        typography = CyberAlertaTypography,
        content = content,
    )
}
