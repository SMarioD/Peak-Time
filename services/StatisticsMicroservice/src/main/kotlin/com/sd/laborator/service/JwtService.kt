package com.sd.laborator.service

import io.jsonwebtoken.Claims
import io.jsonwebtoken.Jwts
import io.jsonwebtoken.security.Keys
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken
import org.springframework.security.core.authority.SimpleGrantedAuthority
import org.springframework.security.core.userdetails.User // Import corect din Spring Security
import org.springframework.stereotype.Service
import java.security.Key
import java.util.*

@Service
class JwtService {
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
    fun getAuthentication(token: String): UsernamePasswordAuthenticationToken {
        val claims = extractAllClaims(token)
        val email = claims.subject
        val authorities = listOf(SimpleGrantedAuthority(claims["rol"].toString()))
        val userDetails = User(email, "", authorities)

        return UsernamePasswordAuthenticationToken(userDetails, null, userDetails.authorities)
    }
}