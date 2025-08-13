package com.sd.laborator.filter

import com.sd.laborator.util.JwtUtil
import org.springframework.cloud.gateway.filter.GatewayFilter
import org.springframework.cloud.gateway.filter.factory.AbstractGatewayFilterFactory
import org.springframework.http.HttpStatus
import org.springframework.stereotype.Component

@Component
class AuthenticationFilter(private val jwtUtil: JwtUtil) : AbstractGatewayFilterFactory<AuthenticationFilter.Config>(Config::class.java) {

    class Config

    override fun apply(config: Config): GatewayFilter {
        return GatewayFilter { exchange, chain ->
            val request = exchange.request
            val path = request.uri.path

            if (path == "/api/v1/auth/register" || path == "/api/v1/auth/login") {
                return@GatewayFilter chain.filter(exchange)
            }

            val authHeader = request.headers.getFirst("Authorization")
            if (authHeader == null || !authHeader.startsWith("Bearer ")) {
                exchange.response.statusCode = HttpStatus.UNAUTHORIZED
                return@GatewayFilter exchange.response.setComplete()
            }

            val token = authHeader.substring(7)

            try {
                if (jwtUtil.validateToken(token)) {
                    val claims = jwtUtil.extractAllClaims(token)
                    val userId = claims["userId"].toString()

                    val modifiedRequest = request.mutate()
                        .header("X-User-Id", userId)
                        .build()

                    return@GatewayFilter chain.filter(exchange.mutate().request(modifiedRequest).build())
                }
            } catch (e: Exception) {
                exchange.response.statusCode = HttpStatus.UNAUTHORIZED
                return@GatewayFilter exchange.response.setComplete()
            }

            exchange.response.statusCode = HttpStatus.UNAUTHORIZED
            return@GatewayFilter exchange.response.setComplete()
        }
    }
}