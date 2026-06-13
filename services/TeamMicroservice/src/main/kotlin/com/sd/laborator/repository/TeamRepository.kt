package com.sd.laborator.repository

import com.sd.laborator.model.Team
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param
import org.springframework.stereotype.Repository

@Repository
interface TeamRepository : JpaRepository<Team, Int> {

    @Query("""
        SELECT t FROM Team t 
        JOIN TeamProject tp ON t.id = tp.teamId 
        WHERE tp.projectId = :projectId
    """)
    fun findAllByProjectId(@Param("projectId") projectId: Int): List<Team>

    fun findAllByTeamLeaderId(teamLeaderId: Int): List<Team>
}