package com.sd.laborator.service

import com.sd.laborator.model.Connection
import com.sd.laborator.model.LoginRequest
import com.sd.laborator.model.RegisterRequest
import com.sd.laborator.repository.UserRepository
import com.sd.laborator.model.User
import com.sd.laborator.repository.ConnectionRepository
import org.springframework.stereotype.Service
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder

@Service
class AuthService(private val userRepository:UserRepository, private val connectionRepository: ConnectionRepository, private val jwtService: JwtService) {
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

    fun loginUser(request: LoginRequest):Pair<User,String>{
        val user=userRepository.findByEmail(request.email)?: throw IllegalArgumentException("Utilizatorul nu a fost gasit.")

        if(!passwordEncoder.matches(request.parola, user.parolaHash))
        {
            throw IllegalArgumentException("Parola incorecta.")
        }

        val token=jwtService.generateToken(user)

        return Pair(user,token)
    }

    fun sendConnectionRequest(senderId:Int,receiverEmail:String){
        val receiver = userRepository.findByEmail(receiverEmail)
            ?:throw java.lang.IllegalArgumentException("Utilizatorul cu emailul $receiverEmail nu a fost gasit.")
        if (senderId == receiver.id)
        {
            throw IllegalArgumentException("Nu va puteti trimite o cerere de conexiune singur.")
        }

        val newConnection = Connection(
            utilizator1Id = senderId,
            utilizator2Id = receiver.id,
            status="asteptare"
        )
        connectionRepository.save(newConnection)
    }

    fun getUserConnections(userId: Int): List<Connection> {
        return connectionRepository.findByUtilizator1IdOrUtilizator2Id(userId, userId)
    }

    fun getUsersDetails(userIds: List<Int>): List<User> {
        return userRepository.findAllById(userIds)
    }
    fun updateConnectionStatus(connectionId: Int, newStatus: String): Connection? {
        val connection = connectionRepository.findById(connectionId)
            .orElseThrow { IllegalArgumentException("Conexiunea ...") }

        if (newStatus == "acceptat") {
            connection.status = newStatus
            return connectionRepository.save(connection)
        } else if (newStatus == "respins") {
            connectionRepository.delete(connection)
            return null
        }

        throw IllegalArgumentException("Status invalid: $newStatus")
    }
    fun findUserByEmail(email: String): User {
        return userRepository.findByEmail(email)
            ?: throw IllegalArgumentException("Utilizatorul cu emailul $email nu a fost gasit.")
    }
}