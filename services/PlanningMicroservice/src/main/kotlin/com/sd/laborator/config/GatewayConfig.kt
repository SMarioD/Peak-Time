package com.sd.laborator.config

import com.sd.laborator.filter.AuthenticationFilter
import org.springframework.cloud.gateway.route.RouteLocator
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration

@Configuration
open class GatewayConfig {

    @Bean
    open fun customRouteLocator(builder: RouteLocatorBuilder, authFilter: AuthenticationFilter): RouteLocator {
        return builder.routes()
            .route("auth-service-route") { r ->
                r.path("/api/v1/auth/**")
                    .filters { f ->
                        f.filter(authFilter.apply(AuthenticationFilter.Config()))
                    }
                    .uri("http://auth-service:8080")
            }
            .route("calendar-service-route") { r ->
                r.path("/api/v1/calendar/**")
                    .filters { f ->
                        f.filter(authFilter.apply(AuthenticationFilter.Config()))
                    }
                    .uri("http://calendar-service:8080")
            }
            .build()
    }
}