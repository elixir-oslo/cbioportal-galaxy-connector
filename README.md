# cBioPortal Galaxy Connector

## Overview

cBioPortal Galaxy Connector is a Python-based application that allows users to export data from cBioPortal to a Galaxy instance. The application processes tab-delimited data, prepares it, and uploads it to a specified Galaxy history.

## Features

- **Environment Configuration**: Configure Galaxy URL via environment variables.
- **Data Preparation**: Process and prepare tab-delimited data for upload.
- **Retry Mechanism**: Retry Galaxy instance creation on connection failure.
- **File Upload**: Upload prepared data to a specified Galaxy history.

## Requirements

- `Python 3.7+`
- `pandas`
- `requests`
- `fastapi`
- `uvicorn`
- `bioblend`
- `cbioportal-core`

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/jCHENEBY/cbioportal-galaxy-connector.git
    cd cbioportal-galaxy-connector
    ```

2. Create a conda environment from the environment file and activate it:
    ```sh
    conda create --name cbioportal-galaxy-connector --file environment.yaml
    conda activate cbioportal-galaxy-connector
    ```

3. Run the application:
    ```sh
    uvicorn main:app --reload --host 0.0.0.0 --port 3001
    ```

## Configuration

Set the `GALAXY_URL` environment variable to specify the Galaxy instance URL:
```sh
export GALAXY_URL='http://your-galaxy-instance-url'
export PYLONE_API_KEY='your-pyclone-api-key'
export PYLONE_DATA_PATH='/path/to/your/data'
```

## Usage

1. Ensure the `GALAXY_URL` environment variable is set.
2. Start the application using the `uvicorn` command mentioned above.
3. Use the provided API endpoints to interact with the application and export data to Galaxy.

## Docker

To build and run the application using Docker:

1. Build the Docker image:
    ```sh
    docker build -t cbioportal-galaxy-connector .
    ```

2. Run the Docker container:
    ```sh
    docker run -p 3001:3001 cbioportal-galaxy-connector
    ```

