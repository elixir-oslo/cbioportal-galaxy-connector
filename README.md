# Galaxy Data Exporter

## Overview

Galaxy Data Exporter is a Python-based application that allows users to export data to a Galaxy instance. The application processes tab-delimited data, prepares it, and uploads it to a specified Galaxy history.

## Features

- **Environment Configuration**: Configure Galaxy URL via environment variables.
- **Data Preparation**: Process and prepare tab-delimited data for upload.
- **Retry Mechanism**: Retry Galaxy instance creation on connection failure.
- **File Upload**: Upload prepared data to a specified Galaxy history.

## Requirements

- Python 3.7+
- `pandas`
- `requests`
- `fastapi`
- `uvicorn`
- `bioblend`

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/galaxy-data-exporter.git
    cd galaxy-data-exporter
    ```

2. Create a conda environment from environment file and activate it:
    ```sh
    conda create --name galaxy-data-exporter --file environment.yml
    conda activate galaxy-data-exporter
    ```

3. Run the application:
    ```sh
    uvicorn main:app --reload --host 0.0.0.0 --port 3001
    ```

## Configuration

Set the `GALAXY_URL` environment variable to specify the Galaxy instance URL:
```sh
export GALAXY_URL='http://your-galaxy-instance-url'
```

## Usage

1. Run the FastAPI application:
    ```sh
    uvicorn main:app --reload
    ```

2. Send a POST request to `/export-to-galaxy` with the following JSON payload:
    ```json
    {
        "galaxyToken": "your_galaxy_api_key",
        "galaxyHistoryName": "your_history_name",
        "data": "tab_delimited_data_string"
    }

## Endpoints

- **POST /export-to-galaxy**: Exports data to the specified Galaxy history.

## Example

```sh
curl -X POST "http://127.0.0.1:8000/export-to-galaxy" -H "Content-Type: application/json" -d '{
    "galaxyToken": "your_galaxy_api_key",
    "galaxyHistoryName": "your_history_name",
    "data": "tab_delimited_data_string"
}'
```

## Docker

### Build Docker Image

1. Build the Docker image:
    ```sh
    docker build -t galaxy-data-exporter .
    ```

### Run Docker Container

1. Run the Docker container:
    ```sh
    docker run -d -p 3001:3001 --name galaxy-data-exporter -e GALAXY_URL='http://your-galaxy-instance-url' galaxy-data-exporter
    ```
   
Inside the container, the application run on port 3001.
The following environment variables can be set:
- `GALAXY_URL`: URL of the Galaxy instance. (Can be on another server)

