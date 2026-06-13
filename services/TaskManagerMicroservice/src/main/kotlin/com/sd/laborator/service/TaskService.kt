package com.sd.laborator.service

import com.sd.laborator.model.Task
import com.sd.laborator.model.TaskRequest
import com.sd.laborator.repository.TaskRepository
import org.springframework.kafka.core.KafkaTemplate
import org.springframework.stereotype.Service
import java.time.LocalDateTime

@Service
class TaskService(
    private val taskRepository: TaskRepository,
    private val kafkaTemplate: KafkaTemplate<String, Any>
) {
    private val taskEventsTopic = "task-events"
    private val restTemplate = org.springframework.web.client.RestTemplate()
    private val teamServiceUrl = "http://team-service:8080/api/v1/teams"

    fun createTask(request: TaskRequest, creatorId: Int): Task {
        val durataPert = (request.timpOptimist + 4 * request.timpProbabil + request.timpPesimist) / 6.0
        val dataSfarsitCalculata = request.dataInceputEstimata.plusHours(durataPert.toLong())

        val newTask = Task(
            projectId = request.projectId,
            teamId = request.teamId,
            atribuitLuiId = request.atribuitLuiId,
            creatDeId = creatorId,
            titlu = request.titlu,
            descriere = request.descriere,
            prioritate = request.prioritate,
            predecesorId = request.predecesorId,
            timpOptimist = request.timpOptimist,
            timpProbabil = request.timpProbabil,
            timpPesimist = request.timpPesimist,
            durataEstimataFinala = durataPert,
            dataInceputEstimata = request.dataInceputEstimata,
            dataSfarsitEstimata = dataSfarsitCalculata,
            status = if (request.predecesorId != null) "blocat" else "in asteptare",
            progres = 0
        )

        val savedTask = taskRepository.save(newTask)
        kafkaTemplate.send(taskEventsTopic, mapOf("eventType" to "TASK_CREATED", "task" to savedTask))
        return savedTask
    }

    fun getTasksByProject(projectId: Int): List<Task> {
        return taskRepository.findAll().filter { it.projectId == projectId }
    }

    fun updateTaskStatus(taskId: Int, newStatus: String, requesterId: Int): Task {
        val task = taskRepository.findById(taskId)
            .orElseThrow { IllegalArgumentException("Sarcina nu a fost gasita.") }

        if (task.atribuitLuiId != requesterId) {
            throw SecurityException("Nu aveti permisiunea de a modifica aceasta sarcina.")
        }

        if (newStatus != "in asteptare" && newStatus != "blocat") {
            task.predecesorId?.let { predId ->
                val predecesor = taskRepository.findById(predId).orElse(null)
                if (predecesor != null && predecesor.status != "finalizat") {
                    throw IllegalStateException(
                        "Sarcina este BLOCATA de '${predecesor.titlu}'. Finalizati predecesorul intai!"
                    )
                }
            }
        }

        task.status = newStatus
        if (newStatus.equals("finalizat", ignoreCase = true)) {
            task.dataFinalizare = LocalDateTime.now()
            task.progres = 100

            val taskuriDependente = taskRepository.findAll().filter { it.predecesorId == task.id }
            taskuriDependente.forEach { depTask ->
                depTask.status = "in asteptare"
                taskRepository.save(depTask)
            }
        }

        val updatedTask = taskRepository.save(task)
        kafkaTemplate.send(
            taskEventsTopic,
            mapOf("eventType" to "STATUS_UPDATED", "task" to updatedTask)
        )
        return updatedTask
    }
    fun updateProgress(taskId: Int, progres: Int, requesterId: Int): Task {
        if (progres < 0 || progres > 100) {
            throw IllegalArgumentException("Progresul trebuie sa fie intre 0 si 100.")
        }

        val task = taskRepository.findById(taskId)
            .orElseThrow { IllegalArgumentException("Sarcina nu a fost gasita.") }

        if (task.atribuitLuiId != requesterId) {
            throw SecurityException("Nu aveti permisiunea de a modifica aceasta sarcina.")
        }

        task.progres = progres
        if (progres == 100 && task.status != "finalizat") {
            task.status = "finalizat"
            task.dataFinalizare = LocalDateTime.now()

            val taskuriDependente = taskRepository.findAll().filter { it.predecesorId == task.id }
            taskuriDependente.forEach { depTask ->
                depTask.status = "in asteptare"
                taskRepository.save(depTask)
            }
        }

        val updatedTask = taskRepository.save(task)
        kafkaTemplate.send(
            taskEventsTopic,
            mapOf("eventType" to "PROGRESS_UPDATED", "task" to updatedTask)
        )
        return updatedTask
    }

    fun getTasksForUser(userId: Int): List<Task> = taskRepository.findAllByAtribuitLuiId(userId)
    fun getTasksCreatedBy(creatorId: Int): List<Task> = taskRepository.findAllByCreatDeId(creatorId)

    fun getTasksByTeam(teamId: Int): List<Task> {
        return taskRepository.findAllByTeamId(teamId)
    }

}