package com.sd.laborator.controller

import com.sd.laborator.model.ShareRequest
import com.sd.laborator.service.ShareService
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/v1/share")
class ShareController(private val shareService:ShareService) {

    @PostMapping
    fun createSHare(@RequestBody request: ShareRequest,@RequestHeader("X-User-ID") userId: Int): ResponseEntity<Any> {
        return try{
            shareService.sharePlan(request,userId)
            ResponseEntity.ok(mapOf("message" to " Planul a fost partajat cu succes."))
        }catch (e: Exception)
        {
            ResponseEntity.badRequest().body(mapOf("error" to e.message))
        }
    }
}