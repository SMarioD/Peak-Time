package com.sd.laborator.model

data class AddMemberRequest(
    val userId: Int,
    val rol: String = "MEMBER"
)