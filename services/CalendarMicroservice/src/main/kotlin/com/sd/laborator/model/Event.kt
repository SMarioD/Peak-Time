package com.sd.laborator.model

import java.time.LocalDateTime
import javax.persistence.*

@Entity
@Table(name="evenimente")
data class Event(
    @Id
    @GeneratedValue(strategy=GenerationType.IDENTITY)
    val id: Int = 0,

    @Column(name="utilizator_id",nullable=false)
    val utilizatorId:Int,

    @Column(name="titlu",nullable=false)
    var titlu:String,

    @Column(name="data_inceput", nullable = false)
    var dataInceput: LocalDateTime,

    @Column(name="data_sfarsit",nullable=false)
    var dataSfarsit: LocalDateTime
)