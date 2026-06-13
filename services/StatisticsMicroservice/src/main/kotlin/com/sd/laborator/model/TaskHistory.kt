package com.sd.laborator.model

import java.time.LocalDateTime
import javax.persistence.*

@Entity
@Table(name = "istoric_sarcini")
data class TaskHistory(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(name = "task_id", nullable = false)
    val taskId: Int,

    @Column(name = "titlu_task", nullable = false)
    val titluTask: String,

    @Column(name = "modificat_de_id", nullable = false)
    val modificatDeId: Int,

    @Column(name = "status_nou", nullable = false)
    val statusNou: String,

    @Column(name = "timestamp", nullable = false)
    val timestamp: LocalDateTime = LocalDateTime.now()
)