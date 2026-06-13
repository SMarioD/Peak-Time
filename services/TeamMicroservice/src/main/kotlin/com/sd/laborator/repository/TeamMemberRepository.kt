package com.sd.laborator.repository

import com.sd.laborator.model.TeamMember
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository

@Repository
interface TeamMemberRepository : JpaRepository<TeamMember, Int> {
    fun findAllByTeamId(teamId: Int): List<TeamMember>
    fun findAllByUserId(userId: Int): List<TeamMember>
    fun existsByTeamIdAndUserId(teamId: Int, userId: Int): Boolean
    fun deleteByTeamIdAndUserId(teamId: Int, userId: Int)
}