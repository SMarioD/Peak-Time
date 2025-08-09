package com.sd.laborator.util

import io.jsonwebtoken.Claims
import io.jsonwebtoken.Jwts
import io.jsonwebtoken.security.Keys
import org.springframework.stereotype.Component
import java.security.Key
import java.util.Date

@Component
class JwtUtil{
    private val secretKey: Key = Keys.hmacShaKeyFor("CheieSecretaFoarteLungaSiComplexaPentruProiectulDeLicenta123".toByteArray())

    fun extractAllClaims(token: String): Claims {
        return Jwts.parserBuilder().setSigningKey(secretKey).build().parseClaimsJws(token).body
    }

    fun isTokenExpired(token: String): Boolean {
        return extractAllClaims(token).expiration.before(Date())
    }

    fun validateToken(token: String): Boolean {
        return !isTokenExpired(token)
    }
}