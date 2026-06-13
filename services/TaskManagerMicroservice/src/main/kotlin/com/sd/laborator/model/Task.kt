package com.sd.laborator.model

import java.time.LocalDateTime
import javax.persistence.*
@Entity
@Table(name="sarcini")
data class Task(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Int = 0,

    @Column(name = "atribuit_lui_id", nullable = false)
    var atribuitLuiId: Int,

    @Column(name = "creat_de_id", nullable = false)
    var creatDeId: Int,

    @Column(name = "project_id", nullable = false)
    var projectId: Int,

    @Column(name = "team_id", nullable = true)
    var teamId: Int? = null,

    @Column(name = "titlu", nullable = false)
    var titlu: String,

    @Column(name = "descriere")
    var descriere: String? = null,

    @Column(name = "status", nullable = false)
    var status: String = "in asteptare",

    @Column(name = "prioritate")
    var prioritate: String = "MEDIE",

    @Column(name = "predecesor_id")
    var predecesorId: Int? = null,

    var timpOptimist: Double = 0.0,
    var timpProbabil: Double = 0.0,
    var timpPesimist: Double = 0.0,
    var durataEstimataFinala: Double = 0.0,

    @Column(name = "data_inceput_estimata")
    var dataInceputEstimata: LocalDateTime? = null,

    @Column(name = "data_sfarsit_estimata")
    var dataSfarsitEstimata: LocalDateTime? = null,

    @Column(name = "progres")
    var progres: Int = 0,

    @Column(name = "data_creare", nullable = false)
    var dataCreare: LocalDateTime = LocalDateTime.now(),

    @Column(name = "data_finalizare")
    var dataFinalizare: LocalDateTime? = null


)