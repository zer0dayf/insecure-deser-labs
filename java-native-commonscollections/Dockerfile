# Java 8 is intentional for compatibility with older ysoserial CommonsCollections gadgets.
FROM maven:3.9-eclipse-temurin-8 AS build
WORKDIR /app
COPY java-native-commonscollections/pom.xml ./pom.xml
RUN mvn -B -q -DskipTests dependency:copy-dependencies -DoutputDirectory=target/dependency
COPY java-native-commonscollections/src ./src
RUN mvn -B -q -DskipTests package

FROM eclipse-temurin:8-jre
# Web input wrapper; running as an unprivileged user.
RUN apt-get update && apt-get install -y --no-install-recommends python3 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -r -u 10001 lab
WORKDIR /app
COPY --from=build /app/target/classes /app/classes
COPY --from=build /app/target/dependency /app/dependency
COPY web/server.py /app/server.py
ENV APP_NAME="Java / Native Commons Collections" \
    LAB_COMMAND="java -cp /app/classes:/app/dependency/* lab.NativeDeserApp"
USER lab
EXPOSE 8080
CMD ["python3", "-u", "/app/server.py"]
