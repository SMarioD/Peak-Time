package com.sd.laborator.repository

import com.sd.laborator.model.UserOAuthToken
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository

@Repository
interface UserOAuthTokenRepository : JpaRepository<UserOAuthToken, Long> {
    fun findByUserIdAndProvider(userId: Int, provider: String): UserOAuthToken?
}