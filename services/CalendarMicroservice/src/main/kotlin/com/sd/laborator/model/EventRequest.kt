package com.sd.laborator.model

import java.time.LocalDateTime

data class EventRequest(

    val titlu: String,
    val dataInceput: LocalDateTime,
    val dataSfarsit: LocalDateTime
)