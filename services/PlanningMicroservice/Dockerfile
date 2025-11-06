FROM eclipse-temurin:11-jre-alpine

WORKDIR /app

COPY target/PlanningMicroservice-1.0-SNAPSHOT.jar app.jar

ENTRYPOINT ["java", "-jar", "app.jar"]