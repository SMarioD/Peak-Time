package com.sd.laborator.repository

import com.sd.laborator.model.EmployeeStats
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository

@Repository
interface EmployeeStatsRepository : JpaRepository<EmployeeStats, Int> {
}