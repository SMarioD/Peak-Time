package com.sd.laborator.service

import com.sd.laborator.model.Event
import com.sd.laborator.model.EventRequest
import com.sd.laborator.repository.EventRepository
import org.springframework.stereotype.Service

@Service
class CalendarService(private val eventRepository: EventRepository) {

    fun createEvent(request: EventRequest, utilizatorId: Int): Event {
        val newEvent = Event(
            utilizatorId = utilizatorId,
            titlu = request.titlu,
            dataInceput = request.dataInceput,
            dataSfarsit = request.dataSfarsit
        )
        return eventRepository.save(newEvent)
    }

    fun getEventsForUser(utilizatorId: Int): List<Event> {
        return eventRepository.findByUtilizatorId(utilizatorId)
    }
}