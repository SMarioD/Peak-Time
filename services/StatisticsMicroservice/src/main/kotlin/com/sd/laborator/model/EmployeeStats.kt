package com.sd.laborator.model

import javax.persistence.Column
import javax.persistence.Entity
import javax.persistence.Id
import javax.persistence.Table

@Entity
@Table(name = "statistici_angajat")
data class EmployeeStats(
    @Id
    @Column(name = "angajat_id", nullable = false)
    val employeeId: Int,

    @Column(name = "taskuri_active", nullable = false)
    var activeTasks: Int = 0,

    @Column(name = "total_taskuri_finalizate", nullable = false)
    var totalTasksCompleted: Int = 0,

    @Column(name = "timp_total_finalizare_ore", nullable = false)
    var totalCompletionHours: Double = 0.0,

    @Column(name = "timp_mediu_finalizare_ore", nullable = false)
    var averageCompletionHours: Double = 0.0
)