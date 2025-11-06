package com.sd.laborator.repository

import com.sd.laborator.model.CalendarShare
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository

@Repository
interface CalendarShareRepository: JpaRepository<CalendarShare, Int> {
    fun findBySharedWithUserId(sharedWithUserId: Int): List<CalendarShare>
}