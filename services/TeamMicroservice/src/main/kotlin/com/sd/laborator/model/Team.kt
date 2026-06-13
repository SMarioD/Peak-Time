package com.sd.laborator.model

import java.time.LocalDateTime
import javax.persistence.*

@Entity
@Table(name = "echipe")
data class Team(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Int = 0,

    @Column(name = "nume", nullable = false)
    var nume: String,

    @Column(name = "descriere")
    var descriere: String? = null,

    @Column(name = "team_leader_id", nullable = false)
    var teamLeaderId: Int,

    @Column(name = "project_id", nullable = true)
    var projectId: Int? = null,

    @Column(name = "data_creare", nullable = false)
    var dataCreare: LocalDateTime = LocalDateTime.now()
)