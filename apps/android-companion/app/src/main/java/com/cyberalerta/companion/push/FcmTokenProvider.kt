package com.cyberalerta.companion.push

import com.google.firebase.messaging.FirebaseMessaging
import kotlin.coroutines.resume
import kotlinx.coroutines.suspendCancellableCoroutine

/** Wraps the Task-based FirebaseMessaging API as a suspend function without
 * pulling in the kotlinx-coroutines-play-services dependency for one call. */
suspend fun fetchCurrentFcmToken(): String? = suspendCancellableCoroutine { continuation ->
    FirebaseMessaging.getInstance().token
        .addOnSuccessListener { token -> continuation.resume(token) }
        .addOnFailureListener { continuation.resume(null) }
}
