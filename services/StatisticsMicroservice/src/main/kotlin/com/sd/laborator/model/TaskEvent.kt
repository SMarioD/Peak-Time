package com.sd.laborator.model

import java.time.LocalDateTime

data class TaskEvent(
    val eventType: String,
    val task: TaskData
)

data class TaskData(
    val id: Int,
    val atribuitLuiId: Int,
    val creatDeId: Int,
    val titlu: String,
    val descriere: String?,
    val status: String,
    val dataCreare: LocalDateTime,
    val dataFinalizare: LocalDateTime?
)