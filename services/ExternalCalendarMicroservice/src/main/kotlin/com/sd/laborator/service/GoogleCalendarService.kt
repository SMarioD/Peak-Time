package com.sd.laborator.service

import com.google.api.client.googleapis.auth.oauth2.GoogleCredential
import com.google.api.client.googleapis.javanet.GoogleNetHttpTransport
import com.google.api.client.json.gson.GsonFactory
import com.google.api.client.util.DateTime
import com.google.api.services.calendar.Calendar
import com.google.api.services.calendar.model.Event
import com.google.api.services.calendar.model.EventDateTime
import com.sd.laborator.model.UserOAuthToken
import com.sd.laborator.repository.UserOAuthTokenRepository
import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Service
import org.springframework.web.client.RestTemplate
import java.time.LocalDateTime
import java.time.ZoneOffset

@Service
open class GoogleCalendarService(private val userOAuthTokenRepository: UserOAuthTokenRepository) {

    @Value("\${spring.security.oauth2.client.registration.google.client-id}")
    private lateinit var clientId: String

    @Value("\${spring.security.oauth2.client.registration.google.client-secret}")
    private lateinit var clientSecret: String

    private val applicationName = "Peak Time External Calendar Sync"
    private val jsonFactory = GsonFactory.getDefaultInstance()
    private val httpTransport = GoogleNetHttpTransport.newTrustedTransport()
    private val restTemplate = RestTemplate()

    private fun buildCredential(token: UserOAuthToken): GoogleCredential {
        return GoogleCredential.Builder()
            .setTransport(httpTransport)
            .setJsonFactory(jsonFactory)
            .setClientSecrets(clientId, clientSecret)
            .build()
            .setAccessToken(token.accessToken)
            .setRefreshToken(token.refreshToken)
    }

    private fun getCalendarClient(token: UserOAuthToken): Calendar {
        val now = LocalDateTime.now()
        val needsRefresh = token.expiresAt == null || token.expiresAt!!.isBefore(now.plusMinutes(5))

        if (needsRefresh) {
            if (token.refreshToken.isNullOrBlank()) {
                println("WARN: Refresh Token lipseste pentru user ${token.userId}. Se incearca cu access token existent.")
            } else {
                println("DEBUG: Token expirat/aproape expirat pentru user ${token.userId}. Se face refresh...")
                try {
                    val credential = buildCredential(token)
                    val refreshed = credential.refreshToken()
                    if (refreshed) {
                        token.accessToken = credential.accessToken
                        token.expiresAt = now.plusSeconds(credential.expiresInSeconds ?: 3600L)
                        token.updatedAt = now
                        userOAuthTokenRepository.save(token)
                        println("DEBUG: Token refreshat cu succes pentru user ${token.userId}.")
                    } else {
                        println("WARN: refreshToken() a returnat false pentru user ${token.userId}.")
                    }
                } catch (e: Exception) {
                    println("ERROR: Refresh esuat pentru user ${token.userId}: ${e.message}")
                }
            }
        }

        val credential = buildCredential(token)
        return Calendar.Builder(httpTransport, jsonFactory, credential)
            .setApplicationName(applicationName)
            .build()
    }

    fun getGoogleCalendarEvents(userId: Int): List<Event> {
        val userToken = userOAuthTokenRepository.findByUserIdAndProvider(userId, "google")
            ?: return emptyList()

        return try {
            val client = getCalendarClient(userToken)
            executeListRequest(client)
        } catch (e: com.google.api.client.googleapis.json.GoogleJsonResponseException) {
            if (e.statusCode == 401) {
                println("DEBUG: 401 la cerere pentru user $userId. Fortam refresh...")
                if (!userToken.refreshToken.isNullOrBlank()) {
                    userToken.expiresAt = LocalDateTime.now().minusHours(1)
                    return try {
                        val freshClient = getCalendarClient(userToken)
                        executeListRequest(freshClient)
                    } catch (e2: Exception) {
                        println("ERROR: Nici dupa refresh fortat nu a mers pentru user $userId: ${e2.message}")
                        emptyList()
                    }
                } else {
                    println("ERROR: 401 si nu exista refresh token pentru user $userId. Necesita reconectare.")
                    emptyList()
                }
            } else {
                println("ERROR: Google API error pentru user $userId: ${e.message}")
                emptyList()
            }
        } catch (e: Exception) {
            println("ERROR: Exceptie neasteptata pentru user $userId: ${e.message}")
            emptyList()
        }
    }

    private fun executeListRequest(client: Calendar): List<Event> {
        val twoMonthsAgo = System.currentTimeMillis() - (60L * 24 * 60 * 60 * 1000)
        val events = client.events().list("primary")
            .setTimeMin(DateTime(twoMonthsAgo))
            .setOrderBy("startTime")
            .setSingleEvents(true)
            .execute()
        return events.items ?: emptyList()
    }

    fun createGoogleCalendarEvent(userId: Int, eventTitle: String, startTime: LocalDateTime, endTime: LocalDateTime): Event {
        val userToken = userOAuthTokenRepository.findByUserIdAndProvider(userId, "google")
            ?: throw IllegalStateException("Token OAuth Google nu a fost gasit pentru utilizator $userId")
        val client = getCalendarClient(userToken)

        val event = Event()
            .setSummary(eventTitle)
            .setStart(EventDateTime()
                .setDateTime(DateTime(startTime.atZone(ZoneOffset.UTC).toInstant().toEpochMilli()))
                .setTimeZone("Europe/Bucharest"))
            .setEnd(EventDateTime()
                .setDateTime(DateTime(endTime.atZone(ZoneOffset.UTC).toInstant().toEpochMilli()))
                .setTimeZone("Europe/Bucharest"))

        return client.events().insert("primary", event).execute()
    }

    fun syncEventsToInternalCalendar(userId: Int) {
        val headers = org.springframework.http.HttpHeaders()
        headers.set("X-User-Id", userId.toString())
        val entity = org.springframework.http.HttpEntity<Any>(headers)

        val existingInternalEvents = try {
            restTemplate.exchange(
                "http://calendar-service:8080/api/v1/calendar/events",
                org.springframework.http.HttpMethod.GET,
                entity,
                object : org.springframework.core.ParameterizedTypeReference<List<Map<String, Any>>>() {}
            ).body ?: emptyList()
        } catch (e: Exception) {
            emptyList<Map<String, Any>>()
        }

        val existingKeys = existingInternalEvents.map { "${it["titlu"]}_${it["dataInceput"]}" }.toSet()
        val googleEvents = getGoogleCalendarEvents(userId)

        googleEvents.forEach { gEvent ->
            try {
                val start = gEvent.start?.dateTime ?: gEvent.start?.date
                val end = gEvent.end?.dateTime ?: gEvent.end?.date
                if (start == null || end == null) return@forEach

                val rawStart = start.toStringRfc3339()
                val startClean = if (rawStart.contains("T")) rawStart.substring(0, 19) else rawStart + "T00:00:00"

                val currentKey = "${gEvent.summary ?: "Eveniment Google"}_$startClean"
                if (existingKeys.contains(currentKey)) return@forEach

                val payload = mapOf(
                    "titlu" to (gEvent.summary ?: "Eveniment Google"),
                    "dataInceput" to startClean,
                    "dataSfarsit" to (if (end.toStringRfc3339().contains("T"))
                        end.toStringRfc3339().substring(0, 19)
                    else
                        end.toStringRfc3339() + "T23:59:59")
                )

                restTemplate.postForObject(
                    "http://calendar-service:8080/api/v1/calendar/events",
                    org.springframework.http.HttpEntity(payload, headers),
                    String::class.java
                )
                println("Automat: Importat '${gEvent.summary}' pentru user $userId")
            } catch (e: Exception) {
                println("Eroare la procesarea unui eveniment pentru user $userId: ${e.message}")
            }
        }
    }
}