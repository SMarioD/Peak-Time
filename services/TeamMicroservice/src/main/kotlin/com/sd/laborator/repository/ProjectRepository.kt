package com.sd.laborator.repository

import com.sd.laborator.model.Project
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param
import org.springframework.stereotype.Repository

@Repository
interface ProjectRepository : JpaRepository<Project, Int> {

    @Query("""
        SELECT DISTINCT p FROM Project p 
        JOIN TeamProject tp ON p.id = tp.projectId 
        JOIN TeamMember tm ON tp.teamId = tm.teamId 
        WHERE tm.userId = :userId
    """)
    fun findProjectsByUserId(@Param("userId") userId: Int): List<Project>
}