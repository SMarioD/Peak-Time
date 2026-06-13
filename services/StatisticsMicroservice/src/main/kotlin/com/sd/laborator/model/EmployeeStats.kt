package com.sd.laborator.model

import javax.persistence.*

@Entity
@Table(name = "statistici_angajat")
data class EmployeeStats(
    @Id
    @Column(name = "angajat_id")
    val employeeId: Int,

    @Column(name = "taskuri_active")
    var activeTasks: Int = 0,

    @Column(name = "total_taskuri_finalizate")
    var totalTasksCompleted: Int = 0,

    @Column(name = "throughput_saptamanal")
    var weeklyThroughput: Int = 0,

    @Column(name = "taskuri_intarziate")
    var delayedTasks: Int = 0,

    @Column(name = "timp_mediu_finalizare_ore")
    var avgCompletionTimeHours: Double = 0.0,

    @Column(name = "scor_performanta")
    var performanceScore: Double = 100.0
)