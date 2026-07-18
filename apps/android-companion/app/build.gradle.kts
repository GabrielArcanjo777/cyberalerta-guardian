plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
    id("org.jetbrains.kotlin.plugin.serialization")
    id("com.google.gms.google-services")
}

android {
    namespace = "com.cyberalerta.companion"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.cyberalerta.companion"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "0.1.0-sprint3"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }

    // Plano Mestre v1.1, Secao 8.5: "variantes dev/staging/prod". Cada uma
    // aponta para um backend diferente e tem application id proprio, entao
    // dev/staging/prod podem ficar instalados lado a lado no mesmo aparelho.
    flavorDimensions += "environment"
    productFlavors {
        create("dev") {
            dimension = "environment"
            applicationIdSuffix = ".dev"
            versionNameSuffix = "-dev"
            // 10.0.2.2 e o alias do emulador Android para o localhost da
            // maquina host — aponta para o backend rodando via
            // `uvicorn main:app --port 8000` fora do emulador.
            buildConfigField("String", "API_BASE_URL", "\"http://10.0.2.2:8000/\"")
        }
        create("staging") {
            dimension = "environment"
            applicationIdSuffix = ".staging"
            versionNameSuffix = "-staging"
            // Troque pelo endereco real do homelab (Secao 10.2 do plano)
            // quando o backend de staging estiver exposto na rede.
            buildConfigField("String", "API_BASE_URL", "\"https://staging.cyberalerta.example/\"")
        }
        create("prod") {
            dimension = "environment"
            // Troque pelo dominio real da VPS de producao (Secao 10.1 do
            // plano) quando ela existir — nao usar o homelab aqui.
            buildConfigField("String", "API_BASE_URL", "\"https://api.cyberalerta.example/\"")
        }
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.15.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.7")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.8.7")
    implementation("androidx.activity:activity-compose:1.9.3")

    implementation(platform("androidx.compose:compose-bom:2024.12.01"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
    debugImplementation("androidx.compose.ui:ui-tooling")

    implementation("androidx.navigation:navigation-compose:2.8.5")

    // Rede: Retrofit + kotlinx.serialization (contrato compartilhado com o
    // backend FastAPI em backend/app/devices e backend/app/notifications).
    implementation("com.squareup.retrofit2:retrofit:2.11.0")
    implementation("com.jakewharton.retrofit:retrofit2-kotlinx-serialization-converter:1.0.0")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.7.3")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.9.0")

    // Armazenamento seguro do session_id (bearer do device) — Secao 6.2/6.3.
    implementation("androidx.security:security-crypto:1.1.0-alpha06")

    // Push (Secao 3.6/4.3/7.2) — usa o BOM, sem pin de versao individual.
    implementation(platform("com.google.firebase:firebase-bom:33.7.0"))
    implementation("com.google.firebase:firebase-messaging-ktx")

    testImplementation("junit:junit:4.13.2")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.9.0")
    testImplementation("io.mockk:mockk:1.13.13")

    androidTestImplementation("androidx.test.ext:junit:1.2.1")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.6.1")
    androidTestImplementation(platform("androidx.compose:compose-bom:2024.12.01"))
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")
    debugImplementation("androidx.compose.ui:ui-test-manifest")
}
