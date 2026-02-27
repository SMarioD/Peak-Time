package com.sd.laborator.model

import javax.persistence.*
import java.time.LocalDateTime

@Entity
@Table(name = "user_oauth_tokens")
data class UserOAuthToken(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(name = "user_id", nullable = false)
    var userId: Int = 0,

    @Column(name = "provider", nullable = false)
    var provider: String = "",

    @Column(name = "access_token", length = 2048, nullable = false)
    var accessToken: String = "",

    @Column(name = "refresh_token", length = 2048)
    var refreshToken: String? = null,

    @Column(name = "expires_at")
    var expiresAt: LocalDateTime? = null,

    @Column(name = "scope", length = 1024)
    var scope: String? = null,

    @Column(name = "updated_at")
    var updatedAt: LocalDateTime = LocalDateTime.now()
)