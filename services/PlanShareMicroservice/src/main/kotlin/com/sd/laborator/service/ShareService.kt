package com.sd.laborator.service

import com.sd.laborator.model.ShareRequest
import org.springframework.stereotype.Service
import org.springframework.web.client.RestTemplate

@Service
class ShareService {

    private val restTemplate = RestTemplate()
    private val calendarServiceUrl="http://calendar-service:8080/api/v1/calendar"

    fun sharePlan(request:ShareRequest,ownerId:Int)
    {
        val hiddenIdsString=request.hiddenEventIds?.joinToString(",")

        val payload=mapOf(
            "ownerUserId" to ownerId,
            "sharedWithUserId" to request.sharedWithUserId,
            "startDate" to request.startDate.toString(),
            "endDate" to request.endDate.toString(),
            "hiddenEventIds" to hiddenIdsString
        )

        try{
            restTemplate.postForObject("$calendarServiceUrl/shares",payload,String::class.java)
        }catch(e:Exception){
            println("Eroare la apelarea CalendarService: ${e.message}")
            throw e
        }
    }
}