FROM maven:3.9-eclipse-temurin-8 AS build
WORKDIR /app
COPY java-jackson-json/pom.xml ./pom.xml
RUN mvn -q -DskipTests dependency:copy-dependencies -DoutputDirectory=target/dependency
COPY java-jackson-json/src ./src
RUN mvn -q -DskipTests package

FROM eclipse-temurin:8-jre
RUN apt-get update && apt-get install -y --no-install-recommends python3 && rm -rf /var/lib/apt/lists/* && useradd -r -u 10001 lab
WORKDIR /app
COPY --from=build /app/target/classes /app/classes
COPY --from=build /app/target/dependency /app/dependency
COPY web/server.py /app/server.py
ENV APP_NAME="Java / Jackson Custom Gadget RCE" LAB_COMMAND="java -cp /app/classes:/app/dependency/* lab.DeserApp"
USER lab
EXPOSE 8080
CMD ["python3", "-u", "/app/server.py"]
