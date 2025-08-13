package com.sd.laborator.model

import javax.persistence.*

@Entity@Table(name="conexiuni")
data class Connection(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Int = 0,

    @Column(name = "utilizator1_id", nullable = false)
    var utilizator1Id: Int,

    @Column(name = "utilizator2_id", nullable = false)
    var utilizator2Id: Int,

    @Column(name = "status", nullable = false)
    var status: String = "asteptare"
)