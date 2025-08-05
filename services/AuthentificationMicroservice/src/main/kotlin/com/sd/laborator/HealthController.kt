package com.sd.laborator

import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RestController

@RestController
class HealthController {
    @GetMapping("/api/v1/auth/health")
    fun checkHealth(): Map<String,String>
    {
        return mapOf("status" to "OK")
    }
}