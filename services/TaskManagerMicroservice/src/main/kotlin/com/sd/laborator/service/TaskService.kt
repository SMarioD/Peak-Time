package com.sd.laborator.service

import com.sd.laborator.model.Task
import com.sd.laborator.model.TaskRequest
import com.sd.laborator.repository.TaskRepository
import org.springframework.stereotype.Service
import java.time.LocalDateTime

@Service
class TaskService(private val taskRepository: TaskRepository) {

    fun createTask(request: TaskRequest): Task {
        val newTask = Task(
            atribuitLuiId = request.atribuitLuiId,
            titlu = request.titlu,
            descriere = request.descriere
        )
        return taskRepository.save(newTask)
    }
    fun getTasksForUser(userId: Int): List<Task> {
            return taskRepository.findAllByAtribuitLuiId(userId)
    }
    fun updateTaskStatus(taskId: Int, newStatus: String): Task {
        val task = taskRepository.findById(taskId)
            .orElseThrow { IllegalArgumentException("Sarcina nu a fost gasita.") }

        task.status = newStatus
        if (newStatus == "finalizat") {
            task.dataFinalizare = LocalDateTime.now()
        }

        return taskRepository.save(task)
    }
}