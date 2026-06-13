package com.sd.laborator.service

import com.sd.laborator.model.*
import com.sd.laborator.repository.ProjectRepository
import com.sd.laborator.repository.TeamMemberRepository
import com.sd.laborator.repository.TeamProjectRepository
import com.sd.laborator.repository.TeamRepository
import org.springframework.kafka.core.KafkaTemplate
import org.springframework.stereotype.Service

@Service
class TeamService(
    private val teamRepository: TeamRepository,
    private val teamMemberRepository: TeamMemberRepository,
    private val projectRepository: ProjectRepository,
    private val kafkaTemplate: KafkaTemplate<String, Any>,
    private val teamProjectRepository: TeamProjectRepository
) {
    private val topic = "team-events"

    fun createTeam(request: TeamRequest, leaderId: Int): Team {
        val team = Team(
            nume = request.nume,
            descriere = request.descriere,
            teamLeaderId = leaderId,
            projectId = request.projectId
        )
        val saved = teamRepository.save(team)

        teamMemberRepository.save(
            TeamMember(teamId = saved.id, userId = leaderId, rol = "LEADER")
        )

        kafkaTemplate.send(topic, mapOf("eventType" to "TEAM_CREATED", "team" to saved))
        return saved
    }

    fun getMyTeams(leaderId: Int): List<Team> =
        teamRepository.findAllByTeamLeaderId(leaderId)

    fun getTeamsByProject(projectId: Int): List<Team> =
        teamRepository.findAllByProjectId(projectId)

    fun getTeamMembers(teamId: Int): List<TeamMember> =
        teamMemberRepository.findAllByTeamId(teamId)

    fun addMember(teamId: Int, request: AddMemberRequest, requesterId: Int): TeamMember {
        val team = teamRepository.findById(teamId)
            .orElseThrow { IllegalArgumentException("Echipa nu a fost găsită.") }

        if (team.teamLeaderId != requesterId) {
            throw SecurityException("Doar team leader-ul poate adăuga membri.")
        }

        if (teamMemberRepository.existsByTeamIdAndUserId(teamId, request.userId)) {
            throw IllegalStateException("Utilizatorul este deja membru al echipei.")
        }

        val member = TeamMember(
            teamId = teamId,
            userId = request.userId,
            rol = request.rol
        )
        val saved = teamMemberRepository.save(member)
        kafkaTemplate.send(topic, mapOf("eventType" to "MEMBER_ADDED", "teamId" to teamId, "userId" to request.userId))
        return saved
    }

    fun removeMember(teamId: Int, userId: Int, requesterId: Int) {
        val team = teamRepository.findById(teamId)
            .orElseThrow { IllegalArgumentException("Echipa nu a fost găsită.") }

        if (team.teamLeaderId != requesterId) {
            throw SecurityException("Doar team leader-ul poate elimina membri.")
        }

        if (userId == team.teamLeaderId) {
            throw IllegalStateException("Nu poți elimina team leader-ul din echipă.")
        }

        teamMemberRepository.deleteByTeamIdAndUserId(teamId, userId)
        kafkaTemplate.send(topic, mapOf("eventType" to "MEMBER_REMOVED", "teamId" to teamId, "userId" to userId))
    }

    fun deleteTeam(teamId: Int, requesterId: Int) {
        val team = teamRepository.findById(teamId)
            .orElseThrow { IllegalArgumentException("Echipa nu a fost găsită.") }

        if (team.teamLeaderId != requesterId) {
            throw SecurityException("Doar team leader-ul poate șterge echipa.")
        }

        teamMemberRepository.findAllByTeamId(teamId).forEach {
            teamMemberRepository.delete(it)
        }
        teamRepository.delete(team)
    }

    fun getMemberIds(teamId: Int): List<Int> =
        teamMemberRepository.findAllByTeamId(teamId).map { it.userId }

    fun getAllProjects(): List<Project> = projectRepository.findAll()

    fun createProject(project: Project): Project = projectRepository.save(project)

    fun getProjectById(id: Int): Project = projectRepository.findById(id)
        .orElseThrow { IllegalArgumentException("Proiectul cu ID $id nu exista.") }
    fun getProjectsForUser(userId: Int): List<Project> {
        return projectRepository.findProjectsByUserId(userId)
    }
    fun linkProjectToTeam(teamId: Int, projectId: Int) {
        val exists = teamProjectRepository.existsByTeamIdAndProjectId(teamId, projectId)
        if (!exists) {
            teamProjectRepository.save(TeamProject(teamId = teamId, projectId = projectId))
        }
    }
}
