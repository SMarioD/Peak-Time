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
            .csrf().disable()
            .authorizeExchange()
            .pathMatchers("/api/v1/auth/login").permitAll()
            .pathMatchers("/api/v1/auth/register").permitAll()
            .pathMatchers("/oauth2/authorization/google").permitAll()
            .pathMatchers("/login/oauth2/code/google").permitAll()
            .pathMatchers("/actuator/**").permitAll()
            .anyExchange().permitAll()
            .and()
            .httpBasic().disable()
            .formLogin().disable()

        return http.build()
    }
}