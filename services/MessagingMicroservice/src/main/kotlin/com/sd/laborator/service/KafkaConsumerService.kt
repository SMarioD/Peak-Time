package com.sd.laborator.service

import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import com.sd.laborator.model.Message
import com.sd.laborator.repository.MessageRepository
import org.springframework.kafka.annotation.KafkaListener
import org.springframework.stereotype.Service

@Service
class KafkaConsumerService(private val messageRepository: MessageRepository) {

    private val objectMapper =jacksonObjectMapper()

    @KafkaListener(topics=["chat_messages"],groupId= "messaging_group")
    fun listen(message:String)
    {
        print("Mesaj primit din Kafka: $message")
        try{
            val messageObject=objectMapper.readValue(message,Message::class.java)
            messageRepository.save(messageObject)
        }
        catch (e:Exception){
            println("Eroare la procesarea mesajului din Kafka: ${e.message}")
        }
    }
}