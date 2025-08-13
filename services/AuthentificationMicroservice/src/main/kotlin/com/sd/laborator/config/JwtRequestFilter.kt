package com.sd.laborator.config

import com.sd.laborator.service.JwtService
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken
import org.springframework.security.core.context.SecurityContextHolder
import org.springframework.security.core.userdetails.User
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource
import org.springframework.stereotype.Component
import org.springframework.web.filter.OncePerRequestFilter
import javax.servlet.FilterChain
import javax.servlet.http.HttpServletRequest
import javax.servlet.http.HttpServletResponse

@Component
class JwtRequestFilter(private val jwtService: JwtService) : OncePerRequestFilter() {

    override fun doFilterInternal(request: HttpServletRequest, response: HttpServletResponse, chain: FilterChain) {
        val authorizationHeader = request.getHeader("Authorization")
        var email: String? = null
        var jwt: String? = null

        if (authorizationHeader != null && authorizationHeader.startsWith("Bearer ")) {
            jwt = authorizationHeader.substring(7)
            try {
                email = jwtService.extractAllClaims(jwt).subject
            } catch (e: Exception) {
                println("Eroare la validarea token-ului: ${e.message}")
            }
        }

        if (email != null && SecurityContextHolder.getContext().authentication == null) {
            try {
                if (jwtService.validateToken(jwt!!)) {
                    val claims = jwtService.extractAllClaims(jwt)
                    val authorities = listOf(claims["rol"].toString())
                    val userDetails = User(email, "", authorities.map { org.springframework.security.core.authority.SimpleGrantedAuthority(it) })

                    val usernamePasswordAuthenticationToken = UsernamePasswordAuthenticationToken(
                        userDetails, null, userDetails.authorities
                    )
                    usernamePasswordAuthenticationToken.details = WebAuthenticationDetailsSource().buildDetails(request)
                    SecurityContextHolder.getContext().authentication = usernamePasswordAuthenticationToken
                }
            } catch (e: Exception) {
                println("Eroare la configurarea contextului de securitate: ${e.message}")
            }
        }
        chain.doFilter(request, response)
    }
}
