package com.sd.laborator.service

import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import com.sd.laborator.model.Message
import com.sd.laborator.repository.MessageRepository
import org.springframework.messaging.simp.SimpMessagingTemplate
import org.springframework.kafka.annotation.KafkaListener
import org.springframework.stereotype.Service

@Service
class KafkaConsumerService(
    private val messageRepository: MessageRepository,
    private val messagingTemplate: SimpMessagingTemplate
) {

    private val objectMapper = jacksonObjectMapper().findAndRegisterModules()

    @KafkaListener(topics = ["chat_messages"], groupId = "messaging_group")
    fun listen(message: String) {
        println("Mesaj primit din Kafka: $message")
        try {
            val messageObject = objectMapper.readValue(message, Message::class.java)

            messageRepository.save(messageObject)

            messagingTemplate.convertAndSend("/topic/messages/${messageObject.receiverId}", messageObject)
            messagingTemplate.convertAndSend("/topic/messages/${messageObject.senderId}", messageObject)

            println("Mesajul pentru userii ${messageObject.receiverId} și ${messageObject.senderId} a fost trimis la broker-ul WebSocket.")

        } catch (e: Exception) {
            println("Eroare la procesarea mesajului din Kafka: ${e.message}")
        }
    }
}