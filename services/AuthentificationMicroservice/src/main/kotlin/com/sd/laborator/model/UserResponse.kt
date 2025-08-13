package com.sd.laborator.model

data class UserResponse(
    val id: Int,
    val email: String,
    val nume: String?,
    val prenume: String?
)