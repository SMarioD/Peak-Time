package com.sd.laborator.service

import com.sd.laborator.model.Message
import com.sd.laborator.model.SendMessageRequest
import com.sd.laborator.repository.MessageRepository
import org.springframework.stereotype.Service

@Service
class MessageService(private val messageRepository: MessageRepository) {

    fun getConversation(userId1: Int, userId2: Int):List<Message>{
        return messageRepository.findBySenderIdAndReceiverIdOrSenderIdAndReceiverIdOrderByTimestampAsc(
            userId1,userId2,
            userId2,userId1
        )
    }
}