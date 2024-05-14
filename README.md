# msrv-prcr: Message Processor Application

## Description
msrv-prcr is a message processing application designed to handle messages from various messaging systems such as RabbitMQ and Kafka. It provides functionalities to consume messages from input queues or topics, process them, and forward the processed messages to output queues or topics.

## Overview
This Dockerfile sets up a container for running the msrv-prcr service in a Docker environment.

## Usage
1. Build the Docker image:
    ```
    docker build -t msrv-prcr .
    ```
2. Run the Docker container:
    ```
    docker run -it --rm --link rabbitmq-service:rabbitmq-service -e RABBITMQ_HOST=rabbitmq-service -e OUTPUT_TOPIC=final_topic msrv-prcr
    ```
3. Monitor the logs for processing information and errors.

## Folder Structure
- `processor.py`: Main script for the msrv-prcr service.
- `ProcessingSystems/`: Contains modules for processing messages.
- `requirements.txt`: Specifies the required Python packages.
- `Dockerfile.msrv-prcr`: Dockerfile for building the Docker image.
- `README.md`: This file.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or features you'd like to add.

## License
[MIT License](LICENSE)
