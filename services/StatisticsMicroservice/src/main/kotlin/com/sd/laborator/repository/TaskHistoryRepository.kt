package com.sd.laborator.repository

import com.sd.laborator.model.TaskHistory
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository

@Repository
interface TaskHistoryRepository : JpaRepository<TaskHistory, Long> {
    fun findAllByTaskIdOrderByTimestampDesc(taskId: Int): List<TaskHistory>
}