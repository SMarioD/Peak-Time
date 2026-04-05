package com.sd.laborator.service

import com.sd.laborator.repository.UserOAuthTokenRepository
import org.springframework.scheduling.annotation.Scheduled
import org.springframework.stereotype.Component

@Component
class AutoSyncTask(
    private val googleCalendarService: GoogleCalendarService,
    private val userOAuthTokenRepository: UserOAuthTokenRepository
) {
    @Scheduled(fixedRate = 60000)
    fun processAllSyncs() {
        val allTokens = userOAuthTokenRepository.findAll()
        allTokens.forEach { token ->
            try {
                googleCalendarService.syncEventsToInternalCalendar(token.userId)
            } catch (e: Exception) {
                if (e.message?.contains("401") == true || e is IllegalStateException) {
                    println("CRITICAL: Sesiune Google expirată/invalidă pentru user ${token.userId}. Sincronizarea este oprită până la reconectare.")
                } else {
                    println("EROARE TEMPORARĂ user ${token.userId}: ${e.message}")
                }
            }
        }
    }
}