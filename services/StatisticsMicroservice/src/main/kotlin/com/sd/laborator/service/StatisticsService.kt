package com.sd.laborator.service

import com.fasterxml.jackson.databind.ObjectMapper
import com.sd.laborator.model.EmployeeStats
import com.sd.laborator.model.ProjectStats
import com.sd.laborator.model.TaskData
import com.sd.laborator.model.TaskEvent
import com.sd.laborator.model.TaskHistory
import com.sd.laborator.repository.EmployeeStatsRepository
import com.sd.laborator.repository.ProjectStatsRepository
import com.sd.laborator.repository.TaskHistoryRepository
import org.springframework.kafka.annotation.KafkaListener
import org.springframework.stereotype.Service
import org.springframework.web.client.RestTemplate
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import java.time.temporal.ChronoUnit

@Service
class StatisticsService(
    private val employeeStatsRepository: EmployeeStatsRepository,
    private val projectStatsRepository: ProjectStatsRepository,
    private val taskHistoryRepository: TaskHistoryRepository
) {
    private val restTemplate = RestTemplate()
    private val objectMapper = ObjectMapper()
        .registerModule(com.fasterxml.jackson.datatype.jsr310.JavaTimeModule())
        .registerModule(com.fasterxml.jackson.module.kotlin.KotlinModule())
        .configure(com.fasterxml.jackson.databind.DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false)

    private val dtf = DateTimeFormatter.ISO_LOCAL_DATE_TIME

    @KafkaListener(topics = ["task-events"], groupId = "statistics_group")
    fun consumeTaskEvent(message: String) {
        try {
            val taskEvent = objectMapper.readValue(message, TaskEvent::class.java)
            val task = taskEvent.task

            updateEmployeeStats(task, taskEvent.eventType)
            updateProjectStats(task)

            val history = TaskHistory(
                taskId = task.id,
                titluTask = task.titlu,
                modificatDeId = task.atribuitLuiId,
                statusNou = task.status,
                timestamp = LocalDateTime.now()
            )
            taskHistoryRepository.save(history)
            println("Istoric salvat pentru task-ul: ${task.titlu}")

        } catch (e: Exception) {
            println("Eroare la procesarea evenimentului: ${e.message}")
        }
    }

    private fun updateProjectStats(task: TaskData) {
        val projectStats = projectStatsRepository.findById(task.projectId)
            .orElse(ProjectStats(projectId = task.projectId))

        val tasksInProject = fetchTasksFromManager(task.projectId)
        val now = LocalDateTime.now()

        projectStats.taskCount = tasksInProject.size
        projectStats.completedTasks = tasksInProject.count { it.status == "finalizat" }

        if (tasksInProject.isNotEmpty()) {
            projectStats.averageProgress = tasksInProject.map { it.progres ?: 0 }.average()
            projectStats.completionPercentage =
                projectStats.completedTasks.toDouble() / projectStats.taskCount * 100.0
        }

        val delayedTasks = tasksInProject.filter { t ->
            t.status != "finalizat" && t.dataSfarsitEstimata != null &&
                    LocalDateTime.parse(t.dataSfarsitEstimata, dtf).isBefore(now)
        }
        projectStats.delayedTaskCount = delayedTasks.size
        projectStats.isDelayed = delayedTasks.isNotEmpty()

        projectStats.totalEstimatedHours = tasksInProject
            .mapNotNull { it.durataEstimataFinala }
            .sum()

        projectStatsRepository.save(projectStats)
        println("Statistici proiect actualizate: ID=${task.projectId}, delayed=${projectStats.isDelayed}")
    }

    private fun updateEmployeeStats(task: TaskData, eventType: String) {
        val stats = employeeStatsRepository.findById(task.atribuitLuiId)
            .orElse(EmployeeStats(employeeId = task.atribuitLuiId))

        when (eventType) {
            "TASK_CREATED" -> {
                stats.activeTasks++
            }
            "STATUS_UPDATED" -> {
                if (task.status == "finalizat" && task.dataFinalizare != null) {
                    stats.activeTasks = maxOf(0, stats.activeTasks - 1)
                    stats.totalTasksCompleted++

                    stats.weeklyThroughput++

                    if (task.dataCreare != null && task.dataFinalizare != null) {
                        try {
                            val creare = LocalDateTime.parse(task.dataCreare, dtf)
                            val finalizare = LocalDateTime.parse(task.dataFinalizare, dtf)
                            val oreFinalizare = ChronoUnit.HOURS.between(creare, finalizare).toDouble()

                            // Medie rulantă
                            val n = stats.totalTasksCompleted.toDouble()
                            stats.avgCompletionTimeHours =
                                ((stats.avgCompletionTimeHours * (n - 1)) + oreFinalizare) / n
                        } catch (_: Exception) { }
                    }

                    val wasLate = task.dataSfarsitEstimata != null && task.dataFinalizare != null &&
                            try {
                                val estimat = LocalDateTime.parse(task.dataSfarsitEstimata, dtf)
                                val finalizat = LocalDateTime.parse(task.dataFinalizare, dtf)
                                finalizat.isAfter(estimat)
                            } catch (_: Exception) { false }

                    if (wasLate) stats.delayedTasks++

                    if (stats.totalTasksCompleted > 0) {
                        val laTimp = stats.totalTasksCompleted - stats.delayedTasks
                        stats.performanceScore = laTimp.toDouble() / stats.totalTasksCompleted * 100.0
                    }
                }
            }
        }
        employeeStatsRepository.save(stats)
    }

    private fun fetchTasksFromManager(projectId: Int): List<TaskData> {
        return try {
            val url = "http://task-service:8080/api/v1/tasks/project/$projectId"
            val response = restTemplate.getForObject(url, Array<TaskData>::class.java)
            response?.toList() ?: emptyList()
        } catch (e: Exception) {
            println("Nu s-au putut prelua task-urile pentru proiect $projectId: ${e.message}")
            emptyList()
        }
    }
    @KafkaListener(topics = ["team-events"], groupId = "statistics_group")
    fun consumeTeamEvent(message: String) {
        try {
            val event = objectMapper.readTree(message)
            val eventType = event.get("eventType").asText()

            when (eventType) {
                "TEAM_CREATED" -> {
                    val teamId = event.get("team").get("id").asInt()
                    println("Statistici: S-a creat echipa $teamId. Inițializăm metricele de grup.")
                }
                "MEMBER_ADDED" -> {
                    val teamId = event.get("teamId").asInt()
                    val userId = event.get("userId").asInt()
                    println("Statistici: Utilizatorul $userId a fost adăugat în echipa $teamId.")
                }
            }
        } catch (e: Exception) {
            println("Eroare la procesarea evenimentului de echipă: ${e.message}")
        }
    }
}