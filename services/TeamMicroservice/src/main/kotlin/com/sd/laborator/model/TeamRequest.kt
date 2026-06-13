package com.sd.laborator.model

data class TeamRequest(
    val nume: String,
    val descriere: String? = null,
    val projectId: Int? = null
)