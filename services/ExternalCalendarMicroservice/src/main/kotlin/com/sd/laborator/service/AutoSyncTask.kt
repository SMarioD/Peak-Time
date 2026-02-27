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
        println("Pornire sincronizare automată pentru toți utilizatorii...")
        val allTokens = userOAuthTokenRepository.findAll()
        allTokens.forEach { token ->
            try {
                googleCalendarService.syncEventsToInternalCalendar(token.userId)
            } catch (e: Exception) {
                println("Eroare la sincronizarea automată pentru user ${token.userId}: ${e.message}")
            }
        }
    }
}