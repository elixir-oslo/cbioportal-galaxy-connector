FROM condaforge/mambaforge

WORKDIR /app

# Copy environment file and create the conda environment
COPY environment.yml .

RUN mamba env create -f environment.yml --name cbiportal-galaxy-connector

# Copy the rest of the application code
COPY . .

# Copy the entrypoint script
COPY entrypoint.sh /entrypoint.sh

# Ensure the entrypoint script is executable
RUN chmod +x /entrypoint.sh

# Expose the application port
EXPOSE 3001

# Use the entrypoint script to start the application
ENTRYPOINT ["/entrypoint.sh"]
