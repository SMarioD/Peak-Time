package com.sd.laborator.repository

import com.sd.laborator.model.Event
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository

@Repository
interface EventRepository : JpaRepository <Event, Int>{
    fun findByUtilizatorId(utilizatorId: Int): List<Event>
}