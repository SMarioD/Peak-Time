package com.sd.laborator.model

import javax.persistence.*

@Entity
@Table(name = "echipa_proiecte")
data class TeamProject(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Int = 0,
    val teamId: Int,
    val projectId: Int
)