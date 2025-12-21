package com.sd.laborator.controller

import com.sd.laborator.model.SyncRequest
import com.sd.laborator.service.SyncService
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/v1/sync")
class SyncController(private val syncService: SyncService) {

    @PostMapping
    fun findCommonAvailability(
        @RequestBody request: SyncRequest,
        @RequestHeader("Authorization") token: String
    ): ResponseEntity<Any> {
        return try {
            val freeSlots = syncService.findFreeSlots(request, token)
            ResponseEntity.ok(freeSlots)
        } catch (e: Exception) {
            ResponseEntity.badRequest().body(mapOf("error" to "Eroare la procesarea cererii de sincronizare: ${e.message}"))
        }
    }
}