FROM openjdk:11-jre-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl

WORKDIR /app

COPY target/CalendarMicroservice-1.0-SNAPSHOT.jar app.jar

ENTRYPOINT ["java", "-jar", "app.jar"]