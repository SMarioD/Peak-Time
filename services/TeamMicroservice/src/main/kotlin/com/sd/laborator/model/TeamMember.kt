package com.sd.laborator.model

import javax.persistence.*

@Entity
@Table(name = "echipa_membri")
data class TeamMember(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Int = 0,

    @Column(name = "team_id", nullable = false)
    var teamId: Int,

    @Column(name = "user_id", nullable = false)
    var userId: Int,

    @Column(name = "rol")
    var rol: String = "MEMBER"
)