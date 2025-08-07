package com.sd.laborator.model

import javax.persistence.*

@Entity
@Table(name = "utilizatori")
data class User(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Int = 0,

    @Column(name = "email", unique = true, nullable = false)
    var email: String = "",

    @Column(name = "parola_hash", nullable = false)
    var parolaHash: String = "",

    @Column(name = "rol", nullable = false)
    var rol: String = "",

    @Column(name = "nume")
    var nume: String? = null,

    @Column(name = "prenume")
    var prenume: String? = null
)