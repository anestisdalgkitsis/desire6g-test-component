# msrv-prcr: Message Processor Application (adapted)

## Description
msrv-prcr is a message processing application designed to handle messages from various messaging systems such as RabbitMQ and Kafka. It provides functionalities to consume messages from input queues or topics, process them, and forward the processed messages to output queues or topics.

## Overview
This Dockerfile sets up a container for running the msrv-prcr service in a Docker environment.

## Usage
0. Setup test env:
    ```
    docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
    
    source venv/bin/activate
    export INPUT_TOPIC="myinput"
    python3 publish.py

    source venv/bin/activate
    export OUTPUT_TOPIC="myoutput"
    python3 subscribe.py
    ```
1. Build the Docker image:
    ```
    sudo docker build -f Dockerfile.msrv-prcr -t msrv-prcr .
    ```
2. Run the Docker container:
    ```
    sudo docker run -it --rm --link rabbitmq:3-management -e RABBITMQ_HOST=3-management -e OUTPUT_TOPIC=myoutput -e INPUT_TOPIC=myinput -e SITE=site1 msrv-prcr
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
