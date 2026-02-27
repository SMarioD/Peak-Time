package com.sd.laborator.controller

import com.sd.laborator.model.UserOAuthToken
import com.sd.laborator.model.UserResponse
import com.sd.laborator.service.GoogleCalendarService
import com.sd.laborator.repository.UserOAuthTokenRepository
import org.springframework.security.core.annotation.AuthenticationPrincipal
import org.springframework.security.oauth2.client.OAuth2AuthorizedClient
import org.springframework.security.oauth2.client.annotation.RegisteredOAuth2AuthorizedClient
import org.springframework.security.oauth2.core.user.OAuth2User
import org.springframework.web.bind.annotation.*
import org.springframework.http.ResponseEntity
import org.springframework.web.client.RestTemplate
import java.time.LocalDateTime
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import javax.servlet.http.Cookie
import javax.servlet.http.HttpServletResponse

@RestController
@RequestMapping("/api/v1/external-calendar")
open class GoogleCalendarController(
    private val googleCalendarService: GoogleCalendarService,
    private val userOAuthTokenRepository: UserOAuthTokenRepository
) {
    private val restTemplate = RestTemplate()
    private val authServiceUrl = "http://auth-service:8080/api/v1/auth"

    @GetMapping("/google/link")
    fun linkGoogleAccount(@RequestParam userId: Int, response: HttpServletResponse) {
        val cookie = Cookie("peak_time_user_id", userId.toString())
        cookie.path = "/"
        cookie.maxAge = 300
        response.addCookie(cookie)
        response.sendRedirect("/oauth2/authorization/google?prompt=consent&access_type=offline")
    }


    @GetMapping("/google/save-token")
    fun saveGoogleToken(
        @RegisteredOAuth2AuthorizedClient("google") authorizedClient: OAuth2AuthorizedClient,
        @AuthenticationPrincipal oauth2User: OAuth2User,
        @CookieValue("peak_time_user_id") userIdFromCookie: String
    ): ResponseEntity<String> {

        val userId = userIdFromCookie.toInt()
        val googleEmail = oauth2User.getAttribute<String>("email")

        val accessToken = authorizedClient.accessToken.tokenValue
        val refreshToken = authorizedClient.refreshToken?.tokenValue
        val expiresAt = authorizedClient.accessToken.expiresAt?.atOffset(ZoneOffset.UTC)?.toLocalDateTime()

        val existingToken = userOAuthTokenRepository.findByUserIdAndProvider(userId, "google")
        val userOAuthToken = existingToken?.apply {
            this.accessToken = accessToken
            this.refreshToken = refreshToken ?: this.refreshToken
            this.expiresAt = expiresAt
            this.updatedAt = LocalDateTime.now()
        } ?: UserOAuthToken(
            userId = userId,
            provider = "google",
            accessToken = accessToken,
            refreshToken = refreshToken,
            expiresAt = expiresAt,
            scope = authorizedClient.accessToken.scopes.joinToString(", ")
        )

        userOAuthTokenRepository.save(userOAuthToken)

        return ResponseEntity.ok("Succes! Contul Google ($googleEmail) a fost legat de contul tău Peak Time (ID: $userId).")
    }

    @GetMapping("/google/callback")
    fun googleOAuth2Callback(
        @RegisteredOAuth2AuthorizedClient("google") authorizedClient: OAuth2AuthorizedClient,
        @AuthenticationPrincipal oauth2User: OAuth2User
    ): ResponseEntity<String> {
        val email = oauth2User.getAttribute<String>("email")
            ?: throw IllegalStateException("Nu s-a putut obține email-ul de la Google.")

        val userResponse = try {
            restTemplate.getForObject(
                "$authServiceUrl/users/search?email=$email",
                UserResponse::class.java
            ) ?: throw Exception("User not found")
        } catch (e: Exception) {
            return ResponseEntity.status(404).body("Eroare: Utilizatorul cu email-ul $email nu este înregistrat în Peak Time.")
        }

        val userId = userResponse.id
        val accessToken = authorizedClient.accessToken.tokenValue
        val refreshToken = authorizedClient.refreshToken?.tokenValue
        val expiresAt = authorizedClient.accessToken.expiresAt?.atOffset(ZoneOffset.UTC)?.toLocalDateTime()

        val existingToken = userOAuthTokenRepository.findByUserIdAndProvider(userId, "google")
        val userOAuthToken = existingToken?.apply {
            this.accessToken = accessToken
            this.refreshToken = refreshToken
            this.expiresAt = expiresAt
            this.updatedAt = LocalDateTime.now()
        } ?: UserOAuthToken(
            userId = userId,
            provider = "google",
            accessToken = accessToken,
            refreshToken = refreshToken,
            expiresAt = expiresAt,
            scope = authorizedClient.accessToken.scopes.joinToString(", ")
        )

        userOAuthTokenRepository.save(userOAuthToken)

        return ResponseEntity.ok("Autentificare Google Calendar reușită pentru $email! Puteți închide această fereastră.")
    }

    @GetMapping("/google/events")
    fun getEvents(@RequestParam userId: Int): ResponseEntity<Any> {
        return try {
            val googleEvents = googleCalendarService.getGoogleCalendarEvents(userId)
            val simplifiedEvents = googleEvents.map { event ->
                mapOf(
                    "id" to event.id,
                    "summary" to event.summary,
                    "start" to event.start?.dateTime?.toString(),
                    "end" to event.end?.dateTime?.toString(),
                    "status" to event.status
                )
            }
            ResponseEntity.ok(simplifiedEvents)
        } catch (e: Exception) {
            ResponseEntity.status(500).body(mapOf("error" to e.message))
        }
    }

    @PostMapping("/google/events")
    fun createEvent(@RequestParam userId: Int, @RequestBody request: Map<String, String>): ResponseEntity<Any> {
        return try {
            val title = request["title"] ?: throw IllegalArgumentException("Titlul este obligatoriu.")
            val formatter = DateTimeFormatter.ISO_LOCAL_DATE_TIME
            val startTime = LocalDateTime.parse(request["startTime"], formatter)
            val endTime = LocalDateTime.parse(request["endTime"], formatter)

            val createdEvent = googleCalendarService.createGoogleCalendarEvent(userId, title, startTime, endTime)
            ResponseEntity.ok(mapOf("message" to "Succes", "id" to createdEvent.id))
        } catch (e: Exception) {
            ResponseEntity.status(500).body(mapOf("error" to e.message))
        }
    }
    @GetMapping("/google/status")
    fun getGoogleStatus(@RequestParam userId: Int): ResponseEntity<Map<String, Any>> {
        val token = userOAuthTokenRepository.findByUserIdAndProvider(userId, "google")
        return if (token != null) {
            ResponseEntity.ok(mapOf("connected" to true, "email" to "Cont conectat"))
        } else {
            ResponseEntity.ok(mapOf("connected" to false))
        }
    }

    @PostMapping("/google/import")
    fun importEvents(@RequestParam userId: Int): ResponseEntity<Any> {
        return try {
            googleCalendarService.syncEventsToInternalCalendar(userId)
            ResponseEntity.ok(mapOf("message" to "Import finalizat."))
        } catch (e: Exception) {
            e.printStackTrace()
            ResponseEntity.status(500).body(mapOf("error" to "Eroare la import: ${e.javaClass.simpleName} - ${e.localizedMessage}"))
        }
    }


}