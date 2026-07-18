package com.cyberalerta.companion.data.remote

import java.io.IOException
import retrofit2.HttpException

/** Thin result wrapper so ViewModels get a display-ready message instead of
 * having to know about HttpException/IOException themselves. */
sealed interface AppResult<out T> {
    data class Success<T>(val data: T) : AppResult<T>
    data class Error(val message: String) : AppResult<Nothing>
}

suspend fun <T> apiCall(block: suspend () -> T): AppResult<T> = try {
    AppResult.Success(block())
} catch (exception: Exception) {
    if (exception is kotlinx.coroutines.CancellationException) throw exception
    AppResult.Error(exception.toUserMessage())
}

private fun Throwable.toUserMessage(): String = when (this) {
    is HttpException -> when (code()) {
        401 -> "Sessao expirada ou revogada. Pareie o aparelho novamente."
        404 -> "Nao encontrado — pode ter expirado ou ja sido usado."
        422 -> "Dados invalidos."
        in 500..599 -> "Erro no servidor. Tente novamente em instantes."
        else -> "Erro inesperado (codigo ${code()})."
    }
    is IOException -> "Sem conexao com o servidor. Verifique a rede."
    else -> "Erro inesperado."
}
