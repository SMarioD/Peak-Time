FROM eclipse-temurin:11-jre-alpine

RUN apk add --no-cache curl

WORKDIR /app

COPY target/PlanShareMicroservice-1.0-SNAPSHOT.jar app.jar

ENTRYPOINT ["java", "-jar", "app.jar"]