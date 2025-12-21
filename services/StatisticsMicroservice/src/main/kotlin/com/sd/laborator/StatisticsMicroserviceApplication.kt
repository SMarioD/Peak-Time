package com.sd.laborator

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication

@SpringBootApplication
open class StatisticsMicroserviceApplication

fun main(args: Array<String>) {
    runApplication<StatisticsMicroserviceApplication>(*args)
}