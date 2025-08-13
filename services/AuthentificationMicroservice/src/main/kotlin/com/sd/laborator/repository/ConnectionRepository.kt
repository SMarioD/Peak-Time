package com.sd.laborator.repository

import com.sd.laborator.model.Connection
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository

@Repository
interface ConnectionRepository : JpaRepository<Connection, Int> {
    fun findByUtilizator1IdOrUtilizator2Id(utilizator1Id: Int, utilizator2Id: Int): List<Connection>
}