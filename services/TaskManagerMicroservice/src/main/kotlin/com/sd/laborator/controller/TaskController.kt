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
    fun createTask(
        @RequestBody request: TaskRequest,
        @RequestHeader("X-User-Id") creatorId: Int
    ): ResponseEntity<Any> {
        return try {
            val newTask = taskService.createTask(request, creatorId)
            ResponseEntity(newTask, HttpStatus.CREATED)
        } catch (e: Exception) {
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(mapOf("error" to e.message))
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
            val updatedTask = taskService.updateTaskStatus(id, request.status, userId)
            ResponseEntity.ok(updatedTask)
        } catch (e: SecurityException) {
            ResponseEntity.status(HttpStatus.FORBIDDEN)
                .body(mapOf("error" to e.message))
        } catch (e: IllegalStateException) {
            ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(mapOf("error" to e.message))
        } catch (e: Exception) {
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(mapOf("error" to e.message))
        }
    }

    @GetMapping("/created-by-me")
    fun getTasksCreatedBy(@RequestHeader("X-User-Id") creatorId: Int): ResponseEntity<Any> {
        return try {
            ResponseEntity.ok(taskService.getTasksCreatedBy(creatorId))
        } catch (e: Exception) {
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build()
        }
    }

    @GetMapping("/project/{projectId}")
    fun getProjectTasks(@PathVariable projectId: Int): ResponseEntity<Any> {
        return try {
            val tasks = taskService.getTasksByProject(projectId)
            ResponseEntity.ok(tasks)
        } catch (e: Exception) {
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build()
        }
    }
    @GetMapping("/project/{projectId}/gantt")
    fun getProjectGantt(@PathVariable projectId: Int): ResponseEntity<Any> {
        return try {
            val tasks = taskService.getTasksByProject(projectId)
            val titluById = tasks.associate { it.id to it.titlu }

            val ganttRows = tasks.map { task ->
                mapOf(
                    "id" to task.id,
                    "titlu" to task.titlu,
                    "atribuitLuiId" to task.atribuitLuiId,
                    "status" to task.status,
                    "prioritate" to task.prioritate,
                    "progres" to task.progres,
                    "dataInceputEstimata" to task.dataInceputEstimata?.toString(),
                    "dataSfarsitEstimata" to task.dataSfarsitEstimata?.toString(),
                    "durataEstimataFinala" to task.durataEstimataFinala,
                    "predecesorId" to task.predecesorId,
                    "predecesorTitlu" to (task.predecesorId?.let { titluById[it] }),
                    "dataFinalizare" to task.dataFinalizare?.toString()
                )
            }

            ResponseEntity.ok(ganttRows)
        } catch (e: Exception) {
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(mapOf("error" to e.message))
        }
    }

    @PatchMapping("/{id}/progress")
    fun updateProgress(
        @PathVariable id: Int,
        @RequestBody body: Map<String, Int>,
        @RequestHeader("X-User-Id") userId: Int
    ): ResponseEntity<Any> {
        return try {
            val progres = body["progres"] ?: return ResponseEntity.badRequest()
                .body(mapOf("error" to "Câmpul 'progres' lipsește"))
            val updatedTask = taskService.updateProgress(id, progres, userId)
            ResponseEntity.ok(updatedTask)
        } catch (e: SecurityException) {
            ResponseEntity.status(HttpStatus.FORBIDDEN).body(mapOf("error" to e.message))
        } catch (e: Exception) {
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(mapOf("error" to e.message))
        }
    }

    @GetMapping("/team/{teamId}/board")
    fun getTeamBoard(@PathVariable teamId: Int): ResponseEntity<Any> {
        return try {
            val tasks = taskService.getTasksByTeam(teamId)
            val board = mapOf(
                "blocat"       to tasks.filter { it.status == "blocat" },
                "in asteptare" to tasks.filter { it.status == "in asteptare" },
                "in progres"   to tasks.filter { it.status == "in progres" },
                "finalizat"    to tasks.filter { it.status == "finalizat" }
            )
            ResponseEntity.ok(board)
        } catch (e: Exception) {
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(mapOf("error" to e.message))
        }
    }

    @GetMapping("/team/{teamId}/workload")
    fun getTeamWorkload(@PathVariable teamId: Int): ResponseEntity<Any> {
        return try {
            val tasks = taskService.getTasksByTeam(teamId)
            val workload = tasks.groupBy { it.atribuitLuiId }
                .map { (userId, userTasks) ->
                    mapOf(
                        "userId"     to userId,
                        "total"      to userTasks.size,
                        "finalizate" to userTasks.count { it.status == "finalizat" },
                        "inProgres"  to userTasks.count { it.status == "in progres" },
                        "blocate"    to userTasks.count { it.status == "blocat" },
                        "tasks"      to userTasks
                    )
                }
            ResponseEntity.ok(workload)
        } catch (e: Exception) {
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(mapOf("error" to e.message))
        }
    }
}