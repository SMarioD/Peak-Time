package com.sd.laborator.service

import com.sd.laborator.model.EventDTO
import com.sd.laborator.model.SyncRequest
import com.sd.laborator.model.TimeSlot
import org.springframework.core.ParameterizedTypeReference
import org.springframework.http.HttpEntity
import org.springframework.http.HttpHeaders
import org.springframework.http.HttpMethod
import org.springframework.stereotype.Service
import org.springframework.web.client.RestTemplate
import java.time.Duration
import java.time.LocalDateTime

@Service
class SyncService {
    private val restTemplate = RestTemplate()

    fun findFreeSlots(request: SyncRequest, token: String): List<TimeSlot> {
        val allBusySlots = mutableListOf<TimeSlot>()
        val headers = HttpHeaders()
        headers.set("Authorization", token)
        headers.set("X-User-Id", request.userIds.first().toString())
        val httpEntity = HttpEntity<String>(headers)

        for (userId in request.userIds.distinct()) {
            val calendarServiceUrl = "http://calendar-service:8080/api/v1/calendar/events?userId=$userId"
            try {
                val responseType = object : ParameterizedTypeReference<List<EventDTO>>() {}
                val response = restTemplate.exchange(calendarServiceUrl, HttpMethod.GET, httpEntity, responseType)
                response.body?.forEach { event ->
                    if (event.dataInceput.isBefore(request.endDate) && event.dataSfarsit.isAfter(request.startDate)) {
                        allBusySlots.add(TimeSlot(event.dataInceput, event.dataSfarsit))
                    }
                }
            } catch (e: Exception) {
                println("Eroare la preluarea calendarului pentru user $userId: ${e.message}")
            }
        }

        val mergedBusySlots = mergeIntervals(allBusySlots)

        val freeSlots = mutableListOf<TimeSlot>()
        var lastEndTime = request.startDate

        for (busySlot in mergedBusySlots) {
            if (busySlot.startTime.isAfter(lastEndTime)) {
                freeSlots.add(TimeSlot(lastEndTime, busySlot.startTime))
            }
            if (busySlot.endTime.isAfter(lastEndTime)) {
                lastEndTime = busySlot.endTime
            }
        }

        if (lastEndTime.isBefore(request.endDate)) {
            freeSlots.add(TimeSlot(lastEndTime, request.endDate))
        }

        return freeSlots.filter {
            Duration.between(it.startTime, it.endTime).toMinutes() >= request.minDurationMinutes
        }
    }

    private fun mergeIntervals(slots: List<TimeSlot>): List<TimeSlot> {
        if (slots.isEmpty()) return emptyList()

        val sortedSlots = slots.sortedBy { it.startTime }

        val merged = mutableListOf<TimeSlot>()
        var currentStart = sortedSlots.first().startTime
        var currentEnd = sortedSlots.first().endTime

        for (i in 1 until sortedSlots.size) {
            val nextSlot = sortedSlots[i]

            if (nextSlot.startTime.isBefore(currentEnd) || nextSlot.startTime == currentEnd) {
                if (nextSlot.endTime.isAfter(currentEnd)) {
                    currentEnd = nextSlot.endTime
                }
            } else {
                merged.add(TimeSlot(currentStart, currentEnd))
                currentStart = nextSlot.startTime
                currentEnd = nextSlot.endTime
            }
        }
        merged.add(TimeSlot(currentStart, currentEnd))
        return merged
    }
}