package com.sd.laborator.model

import javax.validation.constraints.Email
import javax.validation.constraints.NotBlank
import javax.validation.constraints.Size

data class RegisterRequest(
    @field:NotBlank(message = "Numele este obligatoriu.")
    val nume: String,

    @field:NotBlank(message = "Prenumele este obligatoriu.")
    val prenume: String,

    @field:NotBlank(message = "Email-ul nu poate fi gol.")
    @field:Email(message = "Formatul adresei de email este invalid.")
    val email: String,

    @field:NotBlank(message = "Parola este obligatorie.")
    @field:Size(min = 6, message = "Parola trebuie să aibă cel puțin 6 caractere.")
    val parola: String,

    @field:NotBlank(message = "Rolul este obligatoriu.")
    val rol: String
)