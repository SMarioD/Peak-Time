package com.sd.laborator.service

import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import com.sd.laborator.model.EmployeeStats
import com.sd.laborator.model.TaskEvent
import com.sd.laborator.repository.EmployeeStatsRepository
import org.springframework.kafka.annotation.KafkaListener
import org.springframework.stereotype.Service
import java.time.Duration

@Service
class StatisticsService(private val employeeStatsRepository: EmployeeStatsRepository) {

    private val objectMapper = jacksonObjectMapper().findAndRegisterModules()

    @KafkaListener(topics = ["task-events"], groupId = "statistics_group")
    fun consumeTaskEvent(message: String) {
        println("Eveniment de la TaskManager primit: $message")
        try {
            val taskEvent = objectMapper.readValue(message, TaskEvent::class.java)
            val employeeId = taskEvent.task.atribuitLuiId

            val stats = employeeStatsRepository.findById(employeeId)
                .orElse(EmployeeStats(employeeId = employeeId))

            when (taskEvent.eventType) {
                "TASK_CREATED" -> {
                    stats.activeTasks++
                }
                "STATUS_UPDATED" -> {
                    if (taskEvent.task.status == "finalizat" && taskEvent.task.dataFinalizare != null) {
                        stats.activeTasks--
                        stats.totalTasksCompleted++

                        val duration = Duration.between(taskEvent.task.dataCreare, taskEvent.task.dataFinalizare)
                        val hours = duration.toMillis() / 3600000.0 // Convertim milisecunde în ore

                        stats.totalCompletionHours += hours
                        stats.averageCompletionHours = stats.totalCompletionHours / stats.totalTasksCompleted
                    }
                }
            }
            employeeStatsRepository.save(stats)
            println("Statistici actualizate pentru angajatul ID: $employeeId")

        } catch (e: Exception) {
            println("Eroare la procesarea evenimentului de la TaskManager: ${e.message}")
        }
    }
}