package com.sd.laborator.model
import java.time.LocalDateTime

data class ShareRequest (
    val sharedWithUserId: Int,
    val startDate: LocalDateTime,
    val endDate: LocalDateTime,
    val hiddenEventIds:List<Int>?=null
    )