package com.sd.laborator.model

data class RegisterRequest(
    val nume: String,
    val prenume: String,
    val email: String,
    val parola: String,
    val rol: String
)