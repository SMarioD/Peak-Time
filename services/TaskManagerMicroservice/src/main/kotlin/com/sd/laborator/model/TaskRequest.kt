package com.sd.laborator.model

import java.time.LocalDateTime

data class TaskRequest(
    val projectId: Int,
    val teamId: Int? = null,
    val atribuitLuiId: Int,
    val titlu: String,
    val descriere: String?,
    val prioritate: String = "MEDIE",
    val predecesorId: Int? = null,
    val timpOptimist: Double = 0.0,
    val timpProbabil: Double = 0.0,
    val timpPesimist: Double = 0.0,
    val dataInceputEstimata: LocalDateTime
)