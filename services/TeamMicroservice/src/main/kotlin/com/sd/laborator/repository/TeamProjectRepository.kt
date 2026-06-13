package com.sd.laborator.repository

import com.sd.laborator.model.TeamProject
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository

@Repository
interface TeamProjectRepository : JpaRepository<TeamProject, Int> {
    fun existsByTeamIdAndProjectId(teamId: Int, projectId: Int): Boolean
}