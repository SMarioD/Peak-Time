package com.sd.laborator.model

import org.springframework.web.bind.annotation.GetMapping
import java.time.LocalDateTime
import javax.persistence.*

@Entity
@Table(name = "partajari_calendar")
data class CalendarShare
    (
            @Id
            @GeneratedValue(strategy = GenerationType.IDENTITY)
            val id: Int=0,

            @Column(name="owner_user_id",nullable=false)
            val ownerUserId: Int,

            @Column(name = "shared_with_user_id", nullable = false)
            val sharedWithUserId: Int,

            @Column(name = "start_date", nullable = false)
            val startDate: LocalDateTime,

            @Column(name = "end_date", nullable = false)
            val endDate: LocalDateTime,

            @Column(name = "hidden_event_ids", columnDefinition = "TEXT")
            var hiddenEventIds: String? = null
)