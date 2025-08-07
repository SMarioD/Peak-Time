package com.sd.laborator.service

import com.sd.laborator.model.RegisterRequest
import com.sd.laborator.repository.UserRepository
import com.sd.laborator.model.User
import org.springframework.stereotype.Service
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder

@Service
class AuthService(private val userRepository:UserRepository) {
    private val passwordEncoder=BCryptPasswordEncoder()

    fun registerUser(request:RegisterRequest):User{
        val existingUser=userRepository.findByEmail(request.email)
        if(existingUser!=null){
            throw IllegalArgumentException("Emailul ${request.email} este deja inregistrat!")
        }

        val hashedPassword=passwordEncoder.encode(request.parola)
        val newUser = User(
            email = request.email,
            parolaHash = hashedPassword,
            rol = request.rol,
            nume = request.nume,
            prenume = request.prenume
        )

        return userRepository.save(newUser)
    }
}