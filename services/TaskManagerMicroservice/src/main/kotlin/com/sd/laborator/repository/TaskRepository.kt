package com.sd.laborator.repository

import com.sd.laborator.model.Task
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository

@Repository
interface TaskRepository : JpaRepository<Task, Int> {
    fun findAllByAtribuitLuiId(atribuitLuiId: Int): List<Task>
    fun findAllByCreatDeId(creatDeId: Int): List<Task>
    fun findAllByTeamId(teamId: Int): List<Task>
}