package com.sd.laborator.model
import java.time.LocalDateTime
import javax.persistence.*

@Entity
@Table(name="sarcini")
data class Task (
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Int = 0,

    @Column(name = "atribuit_lui_id", nullable = false)
    var atribuitLuiId: Int,

    @Column(name = "titlu", nullable = false)
    var titlu: String,

    @Column(name = "descriere")
    var descriere: String? = null,

    @Column(name = "status", nullable = false)
    var status: String = "in asteptare",

    @Column(name = "data_creare", nullable = false)
    var dataCreare: LocalDateTime = LocalDateTime.now(),

    @Column(name = "data_finalizare")
    var dataFinalizare: LocalDateTime? = null
)