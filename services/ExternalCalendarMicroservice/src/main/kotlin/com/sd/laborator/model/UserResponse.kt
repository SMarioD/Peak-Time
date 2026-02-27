package com.sd.laborator.model

data class UserResponse(
    val id: Int = 0,
    val email: String = "",
    val nume: String? = null,
    val prenume: String? = null
)