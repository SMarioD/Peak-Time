package com.sd.laborator.repository

import com.sd.laborator.model.ProjectStats
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository

@Repository
interface ProjectStatsRepository : JpaRepository<ProjectStats, Int>