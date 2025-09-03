package com.sd.laborator.controller

import com.sd.laborator.model.TaskRequest
import com.sd.laborator.model.TaskStatusRequest
import com.sd.laborator.service.TaskService
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/v1/tasks")
class TaskController(private val taskService: TaskService) {

    @PostMapping
    fun createTask(@RequestBody request: TaskRequest, @RequestHeader("X-User-Id") creatorId: Int): ResponseEntity<Any> {
        return try {
            ResponseEntity(taskService.createTask(request), HttpStatus.CREATED)
        } catch (e: Exception) {
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build()
        }
    }

    @GetMapping("/mytasks")
    fun getMyTasks(@RequestHeader("X-User-Id") userId: Int): ResponseEntity<Any> {
        return try {
            ResponseEntity.ok(taskService.getTasksForUser(userId))
        } catch (e: Exception) {
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build()
        }
    }

    @PutMapping("/{id}")
    fun updateTaskStatus(
        @PathVariable id: Int,
        @RequestBody request: TaskStatusRequest,
        @RequestHeader("X-User-Id") userId: Int
    ): ResponseEntity<Any> {
        return try {
            val updatedTask = taskService.updateTaskStatus(id, request.status)
            ResponseEntity.ok(updatedTask)
        } catch (e: Exception) {
            ResponseEntity.badRequest().body(mapOf("error" to e.message))
        }
    }
}