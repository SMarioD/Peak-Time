package com.sd.laborator.controller

import com.sd.laborator.model.User
import com.sd.laborator.model.RegisterRequest
import com.sd.laborator.service.AuthService
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/v1/auth")
class AuthController (private val authService: AuthService) {
    @PostMapping("/register")
    fun register(@RequestBody request: RegisterRequest): ResponseEntity<Any> {
        return try {
            val registeredUser = authService.registerUser(request)
            val response = mapOf(
                "id" to registeredUser.id,
                "email" to registeredUser.email,
                "message" to "Utilizator inregistrat cu succes."
            )
            ResponseEntity(response, HttpStatus.CREATED)
        } catch (e: IllegalArgumentException) {
            ResponseEntity.status(HttpStatus.CONFLICT).body(mapOf("error" to e.message))
        } catch (e: Exception) {
            println("A apărut o eroare neașteptată: ${e.message}")
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(mapOf("error" to "A aparut o eroare interna."))
        }
    }
}