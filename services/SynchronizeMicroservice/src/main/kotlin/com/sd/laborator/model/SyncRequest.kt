package com.sd.laborator.model

import java.time.LocalDateTime

data class SyncRequest(val userIds: List<Int>,val startDate: LocalDateTime,val endDate: LocalDateTime,val minDurationMinutes: Long)