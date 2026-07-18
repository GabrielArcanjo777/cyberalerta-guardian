package com.cyberalerta.companion.data.security

import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Base64
import java.security.KeyPairGenerator
import java.security.KeyStore
import java.security.PublicKey
import java.security.spec.ECGenParameterSpec

/**
 * Proof-of-possession key (Secao 6.2: "App cria uma chave local no Keystore
 * e envia prova de posse no pairing"). The private key never leaves the
 * Android Keystore (non-exportable); only the public key, base64-encoded,
 * goes to the server as PairDeviceRequest.publicKey.
 *
 * KNOWN GAP (documented in BUILD_NOTES.md, not hidden here): the backend
 * (Sprint 2, Unidades 2-5) stores this public key but does not yet run a
 * signed-challenge verification against it — that hardening is a Sprint 6
 * item, not a Sprint 3 blocker. Generating and submitting the key now means
 * the wiring exists for whenever that check lands.
 */
class DeviceKeyProvider {

    fun getOrCreatePublicKeyBase64(): String {
        val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE).apply { load(null) }
        val publicKey = keyStore.getCertificate(KEY_ALIAS)?.publicKey ?: generateKeyPair()
        return Base64.encodeToString(publicKey.encoded, Base64.NO_WRAP)
    }

    private fun generateKeyPair(): PublicKey {
        val generator = KeyPairGenerator.getInstance(KeyProperties.KEY_ALGORITHM_EC, ANDROID_KEYSTORE)
        val spec = KeyGenParameterSpec.Builder(KEY_ALIAS, KeyProperties.PURPOSE_SIGN)
            .setDigests(KeyProperties.DIGEST_SHA256)
            .setAlgorithmParameterSpec(ECGenParameterSpec("secp256r1"))
            .build()
        generator.initialize(spec)
        return generator.generateKeyPair().public
    }

    private companion object {
        const val ANDROID_KEYSTORE = "AndroidKeyStore"
        const val KEY_ALIAS = "cyberalerta_device_key"
    }
}
