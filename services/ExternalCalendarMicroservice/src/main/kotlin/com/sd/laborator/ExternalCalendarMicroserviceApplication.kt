package com.sd.laborator

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.scheduling.annotation.EnableScheduling

@SpringBootApplication
@EnableScheduling
open class ExternalCalendarMicroserviceApplication

fun main(args: Array<String>) {
    runApplication<ExternalCalendarMicroserviceApplication>(*args)
}