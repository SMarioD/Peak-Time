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

    fun createTask(request: TaskRequest, creatorId: Int): Task {
        val newTask = Task(
            atribuitLuiId = request.atribuitLuiId,
            creatDeId = creatorId,
            titlu = request.titlu,
            descriere = request.descriere
        )
        val savedTask = taskRepository.save(newTask)
        val event = mapOf("eventType" to "TASK_CREATED", "task" to savedTask)
        kafkaTemplate.send(taskEventsTopic, event)

        return savedTask
    }

    fun getTasksForUser(userId: Int): List<Task> {
        return taskRepository.findAllByAtribuitLuiId(userId)
    }

    fun updateTaskStatus(taskId: Int, newStatus: String, requesterId: Int): Task {
        val task = taskRepository.findById(taskId)
            .orElseThrow { IllegalArgumentException("Sarcina nu a fost gasita.") }

        if (task.atribuitLuiId != requesterId) {
            throw SecurityException("Nu aveti permisiunea de a modifica aceasta sarcina.")
        }

        task.status = newStatus
        if (newStatus.equals("finalizat", ignoreCase = true)) {
            task.dataFinalizare = LocalDateTime.now()
        }

        val updatedTask = taskRepository.save(task)
        val event = mapOf("eventType" to "STATUS_UPDATED", "task" to updatedTask)
        kafkaTemplate.send(taskEventsTopic, event)
        println("Eveniment STATUS_UPDATED trimis pentru task-ul ID: ${updatedTask.id}")

        return updatedTask
    }
}