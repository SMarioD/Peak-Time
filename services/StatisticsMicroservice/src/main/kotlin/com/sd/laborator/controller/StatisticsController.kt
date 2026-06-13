package com.sd.laborator.controller

import com.sd.laborator.model.EmployeeStats
import com.sd.laborator.model.TaskHistory
import com.sd.laborator.repository.EmployeeStatsRepository
import com.sd.laborator.repository.ProjectStatsRepository
import com.sd.laborator.repository.TaskHistoryRepository
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/v1/statistics")
class StatisticsController(
    private val employeeStatsRepository: EmployeeStatsRepository,
    private val projectStatsRepository: ProjectStatsRepository,
    private val taskHistoryRepository: TaskHistoryRepository
) {

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
        val fullStats = employeeIds.map { id ->
            teamStats.find { it.employeeId == id } ?: EmployeeStats(employeeId = id)
        }

        return ResponseEntity.ok(fullStats)
    }

    @GetMapping("/project/{projectId}")
    fun getProjectHealth(@PathVariable projectId: Int): ResponseEntity<Any> {
        val stats = projectStatsRepository.findById(projectId)
        return if (stats.isPresent) {
            ResponseEntity.ok(stats.get())
        } else {
            ResponseEntity.notFound().build()
        }
    }

    @GetMapping("/task/{taskId}/history")
    fun getTaskHistory(@PathVariable taskId: Int): ResponseEntity<List<TaskHistory>> {
        return ResponseEntity.ok(taskHistoryRepository.findAllByTaskIdOrderByTimestampDesc(taskId))
    }
}