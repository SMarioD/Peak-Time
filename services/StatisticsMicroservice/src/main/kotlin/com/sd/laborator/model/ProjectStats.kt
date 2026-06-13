package com.sd.laborator.model

import javax.persistence.*

@Entity
@Table(name = "statistici_proiect")
data class ProjectStats(
    @Id
    @Column(name = "proiect_id")
    val projectId: Int,

    @Column(name = "progres_mediu")
    var averageProgress: Double = 0.0,

    @Column(name = "numar_taskuri")
    var taskCount: Int = 0,

    @Column(name = "numar_taskuri_finalizate")
    var completedTasks: Int = 0,

    @Column(name = "estimare_depasita")
    var isDelayed: Boolean = false,

    @Column(name = "numar_taskuri_intarziate")
    var delayedTaskCount: Int = 0,

    @Column(name = "durata_totala_estimata_ore")
    var totalEstimatedHours: Double = 0.0,

    @Column(name = "procent_finalizare")
    var completionPercentage: Double = 0.0
)