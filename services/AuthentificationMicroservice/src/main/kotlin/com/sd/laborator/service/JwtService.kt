package com.sd.laborator.service

import com.sd.laborator.model.User
import io.jsonwebtoken.Jwts
import io.jsonwebtoken.SignatureAlgorithm
import io.jsonwebtoken.security.Keys
import org.springframework.stereotype.Service
import java.security.Key
import java.util.Date

@Service
class JwtService {
    private val secretKey: Key = Keys.hmacShaKeyFor("CheieSecretaFoarteLungaSiComplexaPentruProiectulDeLicenta123".toByteArray())
    fun generateToken(user: User):String{
        val claims: MutableMap<String, Any> = HashMap()
        claims["userId"]=user.id
        claims["rol"]=user.rol
        val creationDate=Date()

        val expirationDate=Date(creationDate.time+10*60*60*1000)

        return Jwts.builder()
            .setClaims(claims)
            .setSubject(user.email)
            .setIssuedAt(creationDate)
            .setExpiration(expirationDate)
            .signWith(secretKey)
            .compact()
    }
}