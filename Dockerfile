FROM maven:3-eclipse-temurin-21 AS jar_builder

# Install git and clone the repository
RUN git clone https://github.com/cBioPortal/cbioportal-core.git /cbioportal-core

# Set the working directory in the Maven image
WORKDIR /app

# Copy the java source files and the pom.xml file into the image
RUN cp -R /cbioportal-core/src ./src
RUN cp /cbioportal-core/pom.xml .

# Build the application
RUN mvn clean package -DskipTests

FROM maven:3-eclipse-temurin-21

# Install git and clone the repository
RUN git clone https://github.com/cBioPortal/cbioportal-core.git /cbioportal-core

# Download system dependencies first to take advantage of docker caching
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        default-mysql-client \
        default-libmysqlclient-dev \
        python3 \
        python3-setuptools \
        python3-dev \
        python3-venv \
        unzip \
        perl \
        wget \
    && rm -rf /var/lib/apt/lists/*

# Create and activate a virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install any needed packages specified in requirements.txt
RUN /opt/venv/bin/pip install --no-cache-dir -r /cbioportal-core/requirements.txt

# Install dependencies from environment.txt
COPY environment.txt .
RUN /opt/venv/bin/pip install --no-cache-dir -r environment.txt

# Copy scripts and make them executable
RUN cp -R /cbioportal-core/scripts/ scripts/
RUN chmod -R a+x /scripts/

# Copy the built JAR file from the first stage
COPY --from=jar_builder /app/core-*.jar /

# Set the working directory in the container
WORKDIR /scripts/

ENV PORTAL_HOME=/

# This file is empty. It has to be overridden by bind mounting the actual application.properties
RUN touch /application.properties

# Copy the rest of the application code to /server
COPY . /server/

# Copy the entrypoint script to /server
COPY entrypoint.sh /server/entrypoint.sh

# Ensure the entrypoint script is executable
RUN chmod +x /server/entrypoint.sh

EXPOSE 3001

ENTRYPOINT ["/server/entrypoint.sh"]