package com.sd.laborator.config

import org.springframework.context.annotation.Configuration
import org.springframework.security.config.annotation.web.builders.HttpSecurity
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity
import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter
import org.springframework.security.oauth2.client.registration.ClientRegistrationRepository
import org.springframework.security.oauth2.client.web.DefaultOAuth2AuthorizationRequestResolver
import org.springframework.security.oauth2.client.web.OAuth2AuthorizationRequestResolver
import org.springframework.security.oauth2.core.endpoint.OAuth2AuthorizationRequest
import javax.servlet.http.HttpServletRequest

@Configuration
@EnableWebSecurity
open class SecurityConfig(
    private val clientRegistrationRepository: ClientRegistrationRepository
) : WebSecurityConfigurerAdapter() {

    override fun configure(http: HttpSecurity) {
        http
            .csrf().disable()
            .authorizeRequests()
            .antMatchers("/**").permitAll()
            .anyRequest().authenticated()
            .and()
            .oauth2Login()
            .authorizationEndpoint()
            .authorizationRequestResolver(customAuthorizationRequestResolver())
            .and()
            .defaultSuccessUrl("/api/v1/external-calendar/google/save-token", true)
            .and()
            .logout()
            .logoutSuccessUrl("/")
    }

    private fun customAuthorizationRequestResolver(): OAuth2AuthorizationRequestResolver {
        val defaultResolver = DefaultOAuth2AuthorizationRequestResolver(
            clientRegistrationRepository,
            "/oauth2/authorization"
        )
        return object : OAuth2AuthorizationRequestResolver {
            override fun resolve(request: HttpServletRequest): OAuth2AuthorizationRequest? =
                defaultResolver.resolve(request)?.let { addOfflineParams(it) }

            override fun resolve(request: HttpServletRequest, clientRegistrationId: String): OAuth2AuthorizationRequest? =
                defaultResolver.resolve(request, clientRegistrationId)?.let { addOfflineParams(it) }
        }
    }

    private fun addOfflineParams(request: OAuth2AuthorizationRequest): OAuth2AuthorizationRequest {
        val extraParams = LinkedHashMap(request.additionalParameters)
        extraParams["access_type"] = "offline"
        extraParams["prompt"] = "consent"
        return OAuth2AuthorizationRequest.from(request)
            .additionalParameters(extraParams)
            .build()
    }
}