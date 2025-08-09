package com.sd.laborator.filter

import com.sd.laborator.util.JwtUtil
import org.springframework.cloud.gateway.filter.GatewayFilter
import org.springframework.cloud.gateway.filter.factory.AbstractGatewayFilterFactory
import org.springframework.http.HttpStatus
import org.springframework.stereotype.Component

@Component
class AuthenticationFilter(private val jwtUtil: JwtUtil) : AbstractGatewayFilterFactory<AuthenticationFilter.Config>(Config::class.java) {

    class Config {}

    override fun apply(config: Config): GatewayFilter {
        return GatewayFilter{
            exchange, chain ->
            val request=exchange.request
            val response = exchange.response

            if (request.uri.path.contains("/auth")) {
                return@GatewayFilter chain.filter(exchange)
            }

            val authHeader = request.headers.getFirst("Authorization")
            if (authHeader == null || !authHeader.startsWith("Bearer ")) {
                response.statusCode = HttpStatus.UNAUTHORIZED
                return@GatewayFilter response.setComplete()
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
                response.statusCode = HttpStatus.UNAUTHORIZED
                return@GatewayFilter response.setComplete()
            }

            response.statusCode = HttpStatus.UNAUTHORIZED
            return@GatewayFilter response.setComplete()
        }
    }
}