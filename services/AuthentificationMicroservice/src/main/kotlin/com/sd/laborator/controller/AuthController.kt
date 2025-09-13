package com.sd.laborator.controller

import com.sd.laborator.model.ConnectionRequest
import com.sd.laborator.model.User
import com.sd.laborator.model.LoginRequest
import com.sd.laborator.model.RegisterRequest
import com.sd.laborator.model.UserResponse
import com.sd.laborator.service.AuthService
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.RequestParam
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.PutMapping
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController
import org.springframework.web.bind.annotation.RequestHeader


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


    @PostMapping("/login")
    fun login(@RequestBody request: LoginRequest): ResponseEntity<Any> {
        return try{
            val (user, token) = authService.loginUser(request)

            val response=mapOf(
                "userId" to user.id,
                "rol" to user.rol,
                "token" to token,
                "message" to "Authentificare reusita."
            )
            ResponseEntity.ok(response)
        }
        catch (e: IllegalArgumentException)
        {
            ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(mapOf("error" to e.message))
        }catch (e: Exception) {
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(mapOf("error" to "A aparut o eroare interna."))
        }
    }

    @PostMapping("/connections")
    fun sendConnectionRequest(@RequestBody request: ConnectionRequest, @RequestHeader("X-User-Id") senderId: Int): ResponseEntity<Any> {
        return try {
            authService.sendConnectionRequest(senderId, request.email)
            ResponseEntity.ok(mapOf("message" to "Cerere de conexiune trimisa cu succes."))
        } catch (e: Exception) {
            ResponseEntity.badRequest().body(mapOf("error" to e.message))
        }
    }

    @GetMapping("/connections")
    fun getConnections(@RequestHeader("X-User-Id") userId: Int): ResponseEntity<Any> {
        return try {
            val connections = authService.getUserConnections(userId)
            ResponseEntity.ok(connections)
        } catch (e: Exception) {
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(mapOf("error" to e.message))
        }
    }

    @PutMapping("/connections/{id}")
    fun updateConnection(@PathVariable id: Int, @RequestBody statusUpdate: Map<String, String>): ResponseEntity<Any> {
        return try {
            val newStatus = statusUpdate["status"] ?: throw IllegalArgumentException("Statusul este obligatoriu.")
            val updatedConnection = authService.updateConnectionStatus(id, newStatus)
            ResponseEntity.ok(updatedConnection)
        } catch (e: Exception) {
            ResponseEntity.badRequest().body(mapOf("error" to e.message))
        }
    }

    @PostMapping("/users/details")
    fun getUsersDetails(@RequestBody userIds: List<Int>): ResponseEntity<Any> {
        return try {
            val users = authService.getUsersDetails(userIds)
            val response = users.map { user ->
                UserResponse(id = user.id, email = user.email, nume = user.nume, prenume = user.prenume)
            }
            ResponseEntity.ok(response)
        } catch (e: Exception) {
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(mapOf("error" to "Nu s-au putut prelua detaliile utilizatorilor."))
        }
    }

    @GetMapping("/users/search")
    fun searchUserByEmail(@RequestParam email: String): ResponseEntity<Any> {
        return try {
            val user = authService.findUserByEmail(email)
            val response = UserResponse(id = user.id, email = user.email, nume = user.nume, prenume = user.prenume)
            ResponseEntity.ok(response)
        } catch (e: IllegalArgumentException) {
            ResponseEntity.status(HttpStatus.NOT_FOUND).body(mapOf("error" to e.message))
        }
    }
}