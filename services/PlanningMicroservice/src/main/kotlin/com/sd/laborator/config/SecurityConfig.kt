package com.sd.laborator.config

import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.security.config.web.server.ServerHttpSecurity
import org.springframework.security.web.server.SecurityWebFilterChain

@Configuration
open class SecurityConfig {

    @Bean
    open fun springSecurityFilterChain(http: ServerHttpSecurity): SecurityWebFilterChain {
        http
            .authorizeExchange { exchanges -> exchanges.anyExchange().permitAll() }
            .csrf { csrf -> csrf.disable() }
        return http.build()
    }
}