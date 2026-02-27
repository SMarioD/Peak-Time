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
            .route("task-service-route") { r ->
                r.path("/api/v1/tasks/**")
                    .filters { f ->
                        f.filter(authFilter.apply(AuthenticationFilter.Config()))
                    }
                    .uri("http://task-service:8080")
            }
            .route("messaging-service-route") { r ->
                r.path("/api/v1/messages/**")
                    .filters { f ->
                        f.filter(authFilter.apply(AuthenticationFilter.Config()))
                    }
                    .uri("http://messaging-service:8080")
            }
            .route("messaging-service-websocket-route") { r ->
                r.path("/ws/**")
                    .uri("ws://messaging-service:8080")
            }
            .route("planshare-service-route") { r ->
                r.path("/api/v1/share/**")
                    .filters { f ->
                        f.filter(authFilter.apply(AuthenticationFilter.Config()))
                    }
                    .uri("http://planshare-service:8080")
            }
            .route("synchronize-service-route") { r ->
                r.path("/api/v1/sync/**")
                    .filters { f ->
                        f.filter(authFilter.apply(AuthenticationFilter.Config()))
                    }
                    .uri("http://synchronize-service:8080")
            }
            .route("statistics-service-route") { r ->
                r.path("/api/v1/statistics/**")
                    .filters { f ->
                        f.filter(authFilter.apply(AuthenticationFilter.Config()))
                    }
                    .uri("http://statistics-service:8080")
            }
            .route("external-calendar-service-route") { r ->
                r.path("/api/v1/external-calendar/**")
                    .filters { f ->
                        f.filter(authFilter.apply(AuthenticationFilter.Config()))
                    }
                    .uri("http://external-calendar-service:8080")
            }
            .route("google-oauth2-callback") { r ->
                r.path("/login/oauth2/code/google")
                    .uri("http://external-calendar-service:8080")
            }
            .route("google-oauth2-init") { r ->
                r.path("/oauth2/authorization/google")
                    .filters { f ->
                        f
                    }
                    .uri("http://external-calendar-service:8080")
            }
            .build()
    }
}