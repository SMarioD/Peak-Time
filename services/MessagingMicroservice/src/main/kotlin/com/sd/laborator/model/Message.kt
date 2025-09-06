package com.sd.laborator.model

import java.time.LocalDateTime
import javax.persistence.*

@Entity
@Table(name="mesaje")
data class Message(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Int=0,

    @Column(name="sender_id",nullable=false)
    val senderId:Int,

    @Column(name="receiver_id", nullable = false)
    val receiverId:Int,

    @Column(name="continut", nullable = false, columnDefinition = "TEXT")
    val continut: String,

    @Column(name = "timestamp", nullable = false)
    val timestamp: LocalDateTime=LocalDateTime.now()
)