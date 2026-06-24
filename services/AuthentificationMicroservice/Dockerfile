FROM eclipse-temurin:11-jre-alpine

WORKDIR /app

COPY target/AuthentificationMicroservice-1.0-SNAPSHOT.jar app.jar

ENTRYPOINT ["java", "-jar", "app.jar"]