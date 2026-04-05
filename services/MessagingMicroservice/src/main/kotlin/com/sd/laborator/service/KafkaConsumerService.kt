package com.sd.laborator.service

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
    @KafkaListener(topics = ["chat_messages"], groupId = "messaging_group")
    fun listen(messageObject: Message) {
        try {
            println("Mesaj primit pentru salvare: ${messageObject.continut}")

            messageRepository.save(messageObject)
            messagingTemplate.convertAndSend("/topic/messages/${messageObject.receiverId}", messageObject)
            messagingTemplate.convertAndSend("/topic/messages/${messageObject.senderId}", messageObject)

            println("Succes: Mesaj procesat și distribuit.")
        } catch (e: Exception) {
            println("Eroare la procesarea mesajului: ${e.message}")
        }
    }
}