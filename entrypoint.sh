#!/bin/bash
source activate cbiportal-galaxy-connector

# Get the Docker subnet
DOCKER_SUBNET=$(hostname -I | awk '{print $1}' | grep -Eo '^[0-9]+\.[0-9]+\.[0-9]+')

# Export the Docker subnet as an environment variable
export DOCKER_SUBNET

# Ensure the environment variable is available to the shell
echo "export DOCKER_SUBNET=$DOCKER_SUBNET" >> ~/.bashrc

cd /
exec uvicorn app.main:app --host 0.0.0.0 --port 3001 --log-level info --log-config /app/logging_config.yaml --reload --reload-dir app