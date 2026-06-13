package com.sd.laborator.controller

import com.sd.laborator.model.AddMemberRequest
import com.sd.laborator.model.Project
import com.sd.laborator.model.TeamRequest
import com.sd.laborator.service.TeamService
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/v1/teams")
class TeamController(private val teamService: TeamService) {

    @PostMapping
    fun createTeam(
        @RequestBody request: TeamRequest,
        @RequestHeader("X-User-Id") leaderId: Int
    ): ResponseEntity<Any> = try {
        ResponseEntity(teamService.createTeam(request, leaderId), HttpStatus.CREATED)
    } catch (e: Exception) {
        ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(mapOf("error" to e.message))
    }

    @GetMapping("/my-teams")
    fun getMyTeams(@RequestHeader("X-User-Id") leaderId: Int): ResponseEntity<Any> = try {
        ResponseEntity.ok(teamService.getMyTeams(leaderId))
    } catch (e: Exception) {
        ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build()
    }

    @GetMapping("/project/{projectId}")
    fun getTeamsByProject(@PathVariable projectId: Int): ResponseEntity<Any> = try {
        ResponseEntity.ok(teamService.getTeamsByProject(projectId))
    } catch (e: Exception) {
        ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build()
    }

    @GetMapping("/{teamId}/members")
    fun getMembers(@PathVariable teamId: Int): ResponseEntity<Any> = try {
        ResponseEntity.ok(teamService.getTeamMembers(teamId))
    } catch (e: Exception) {
        ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build()
    }

    // Endpoint intern pentru TaskManager
    @GetMapping("/{teamId}/member-ids")
    fun getMemberIds(@PathVariable teamId: Int): ResponseEntity<Any> = try {
        ResponseEntity.ok(teamService.getMemberIds(teamId))
    } catch (e: Exception) {
        ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build()
    }

    @PostMapping("/{teamId}/members")
    fun addMember(
        @PathVariable teamId: Int,
        @RequestBody request: AddMemberRequest,
        @RequestHeader("X-User-Id") requesterId: Int
    ): ResponseEntity<Any> = try {
        ResponseEntity(teamService.addMember(teamId, request, requesterId), HttpStatus.CREATED)
    } catch (e: SecurityException) {
        ResponseEntity.status(HttpStatus.FORBIDDEN).body(mapOf("error" to e.message))
    } catch (e: IllegalStateException) {
        ResponseEntity.status(HttpStatus.CONFLICT).body(mapOf("error" to e.message))
    } catch (e: Exception) {
        ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(mapOf("error" to e.message))
    }

    @DeleteMapping("/{teamId}/members/{userId}")
    fun removeMember(
        @PathVariable teamId: Int,
        @PathVariable userId: Int,
        @RequestHeader("X-User-Id") requesterId: Int
    ): ResponseEntity<Any> = try {
        teamService.removeMember(teamId, userId, requesterId)
        ResponseEntity.ok(mapOf("message" to "Membrul a fost eliminat."))
    } catch (e: SecurityException) {
        ResponseEntity.status(HttpStatus.FORBIDDEN).body(mapOf("error" to e.message))
    } catch (e: Exception) {
        ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(mapOf("error" to e.message))
    }

    @DeleteMapping("/{teamId}")
    fun deleteTeam(
        @PathVariable teamId: Int,
        @RequestHeader("X-User-Id") requesterId: Int
    ): ResponseEntity<Any> = try {
        teamService.deleteTeam(teamId, requesterId)
        ResponseEntity.ok(mapOf("message" to "Echipa a fost ștearsă."))
    } catch (e: SecurityException) {
        ResponseEntity.status(HttpStatus.FORBIDDEN).body(mapOf("error" to e.message))
    } catch (e: Exception) {
        ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(mapOf("error" to e.message))
    }

    @GetMapping("/projects")
    fun getAllProjects(): ResponseEntity<List<Project>> {
        return ResponseEntity.ok(teamService.getAllProjects())
    }

    @PostMapping("/projects")
    fun createProject(@RequestBody project: Project): ResponseEntity<Project> {
        return ResponseEntity.status(HttpStatus.CREATED).body(teamService.createProject(project))
    }

    @GetMapping("/my-projects")
    fun getMyProjects(@RequestHeader("X-User-Id") userId: Int): ResponseEntity<List<Project>> {
        return ResponseEntity.ok(teamService.getProjectsForUser(userId))
    }

    @PostMapping("/{teamId}/projects/{projectId}")
    fun linkProject(@PathVariable teamId: Int, @PathVariable projectId: Int): ResponseEntity<Any> {
        return try {
            teamService.linkProjectToTeam(teamId, projectId)
            ResponseEntity.ok(mapOf("message" to "Proiectul a fost legat de echipă."))
        } catch (e: Exception) {
            ResponseEntity.badRequest().body(mapOf("error" to e.message))
        }
    }

}