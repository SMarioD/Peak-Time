package com.sd.laborator.controller

import com.sd.laborator.model.EventRequest
import com.sd.laborator.model.CalendarShare
import com.sd.laborator.service.CalendarService
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*
import org.springframework.web.bind.annotation.RequestHeader

@RestController
@RequestMapping("/api/v1/calendar")
class CalendarController (private val calendarService: CalendarService) {
    @PostMapping("/events")
    fun createEvent(@RequestBody request: EventRequest, @RequestHeader("X-User-Id") userId: Int): ResponseEntity<Any> {
        return try {
            val newEvent = calendarService.createEvent(request, userId)
            ResponseEntity(newEvent, HttpStatus.CREATED)
        }catch (e: Exception)
        {
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(mapOf("error" to "A aparut o eroare la cererea evenimentului."))
        }
    }

    @GetMapping("/events")
    fun getEvents(
        @RequestHeader("X-User-Id") requesterId: Int,
        @RequestParam(name = "userId", required = false) targetUserId: Int?
    ): ResponseEntity<Any> {
        return try {
            val userIdToFetch = targetUserId ?: requesterId
            val events = calendarService.getEventsForUser(userIdToFetch)
            ResponseEntity.ok(events)
        } catch (e: Exception) {
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(mapOf("error" to "A aparut o eroare la preluarea evenimentelor."))
        }
    }

    @PostMapping("/shares")
    fun createShare(@RequestBody share: CalendarShare):ResponseEntity<Any>{
        return try {
            val newShare = calendarService.createShare(share)
            ResponseEntity(newShare, HttpStatus.CREATED)
        } catch(e:Exception)
        {
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(mapOf("error" to "Eroare la crearea partajarii."))
        }
    }

    @GetMapping("shares")
    fun getSHares(@RequestHeader("X-User-Id") userId: Int): ResponseEntity<Any> {
        return try{
            val shares= calendarService.getSharesForUser(userId)
            ResponseEntity.ok(shares)
        }catch (e: Exception){
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(mapOf("error" to "Eroare la preluarea partajarilor."))
        }
    }
}