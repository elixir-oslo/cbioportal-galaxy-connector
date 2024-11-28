#!/bin/bash
source activate cbiportal-galaxy-connector

# Get the Docker subnet
DOCKER_SUBNET=$(hostname -I | awk '{print $1}' | grep -Eo '^[0-9]+\.[0-9]+\.[0-9]+')

# Export the Docker subnet as an environment variable
export DOCKER_SUBNET

# Ensure the environment variable is available to the shell
echo "export DOCKER_SUBNET=$DOCKER_SUBNET" >> ~/.bashrc

cd /

# Create the /app/ssl directory if it does not exist
mkdir -p /app/ssl

# Default PROD to false if not set
PROD=${PROD:-false}

# Convert PROD to lowercase
PROD=$(echo "$PROD" | tr '[:upper:]' '[:lower:]')

# Default SSL key and certificate filenames if not set
SSL_KEYFILE_NAME=${SSL_KEYFILE_NAME:-private.key}
SSL_CERTFILE_NAME=${SSL_CERTFILE_NAME:-certificate.crt}

# Check if running in production and if SSL certificates are available
if [[ "$PROD" == "true" && -f "/app/ssl/$SSL_KEYFILE_NAME" && -f "/app/ssl/$SSL_CERTFILE_NAME" ]]; then
    exho "Running in production mode with SSL enabled"
    exec uvicorn app.main:app --host 0.0.0.0 --port 3001 --ssl-keyfile "/app/ssl/$SSL_KEYFILE_NAME" --ssl-certfile "/app/ssl/$SSL_CERTFILE_NAME" --log-level debug --log-config /app/logging_config.yaml --reload --reload-dir app
else
    exec uvicorn app.main:app --host 0.0.0.0 --port 3001 --log-level info --log-config /app/logging_config.yaml --reload --reload-dir app
fi