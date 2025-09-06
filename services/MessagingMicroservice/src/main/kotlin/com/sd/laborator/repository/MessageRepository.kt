package com.sd.laborator.repository

import com.sd.laborator.model.Message
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository

@Repository
interface MessageRepository: JpaRepository<Message, Int> {
    fun findBySenderIdAndReceiverIdOrSenderIdAndReceiverIdOrderByTimestampAsc(
        senderId1:Int,receiverId1:Int,
        senderId2:Int,receiverId2:Int
    ):List<Message>
}