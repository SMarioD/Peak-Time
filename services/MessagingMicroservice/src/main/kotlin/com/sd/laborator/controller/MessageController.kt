package com.sd.laborator.controller

import com.sd.laborator.model.SendMessageRequest
import com.sd.laborator.service.MessageService
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/v1/messages")
class MessageController( private val messageService: MessageService) {

    @PostMapping
    fun sendMessage(@RequestHeader("X-User-Id") senderId: Int, @RequestBody request: SendMessageRequest): ResponseEntity<Any> {
        return try {
            val message = messageService.sendMessage(senderId, request)
            ResponseEntity(message, HttpStatus.CREATED)
        } catch (e: Exception)
        {
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(mapOf("error" to "Eroare la trimiterea mesajului: ${e.message}"))
        }
    }

    @GetMapping("/{partnerId}")
    fun getConversation(@RequestHeader("X-User-Id") userId: Int, @PathVariable partnerId: Int):ResponseEntity<Any>
    {
        return try {
            val conversation = messageService.getConversation(userId, partnerId)
            ResponseEntity.ok(conversation)
        } catch (e: Exception)
        {
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(mapOf("error" to "Eroare la preluarea conversatiei: ${e.message}"))
        }
    }
}