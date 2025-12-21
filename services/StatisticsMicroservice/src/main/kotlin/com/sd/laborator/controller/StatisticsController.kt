package com.sd.laborator.controller

import com.sd.laborator.repository.EmployeeStatsRepository
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/v1/statistics")
class StatisticsController(private val employeeStatsRepository: EmployeeStatsRepository) {

    @GetMapping("/workload/{employeeId}")
    fun getEmployeeWorkload(@PathVariable employeeId: Int): ResponseEntity<Any> {
        val stats = employeeStatsRepository.findById(employeeId)
        return if (stats.isPresent) {
            ResponseEntity.ok(stats.get())
        } else {
            ResponseEntity.notFound().build()
        }
    }
    @GetMapping("/team-performance")
    fun getTeamPerformance(@RequestParam("employeeIds") employeeIds: List<Int>): ResponseEntity<Any> {
        val teamStats = employeeStatsRepository.findAllById(employeeIds)
        return ResponseEntity.ok(teamStats)
    }
}