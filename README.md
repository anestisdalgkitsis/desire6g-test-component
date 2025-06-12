# msrv-prcr: Optimization Engine Desire6G Module

Based on Message Processor Application by NUBIS

## Description

msrv-prcr is a message processing application designed to handle messages from various messaging systems such as RabbitMQ and Kafka. It provides functionalities to consume messages from input queues or topics, process them, and forward the processed messages to output queues or topics.

## Overview

This Dockerfile sets up a container for running the msrv-prcr service in a Docker environment.

## Demo Environment

0. Setup test env:
   Start a RabbitMQ server:

   ```
   docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
   ```

   Open a window (1) to send the request (simulate the SO and IBN functionality).
   You will need the "demo_nsd.sg.yml" in this folder.

   ```
   source venv/bin/activate
   export INPUT_TOPIC="myinput"
   ```

   Open another window (2) to receive the optimized request from the OE (simulate the SO).

   ```
   source venv/bin/activate
   export OUTPUT_TOPIC="myoutput"
   python3 subscribe.py
   ```

   Start Topology + add demo SITEID1 from another window (3)

   ```
   git clone https://github.com/nubispc/desire6g-topology.git
   cd desire6g-topology
   python3 -m venv venv
   source venv/bin/activate
   pip install fastapi uvicorn
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   curl -X 'POST' \
   'http://localhost:8000/nodes/' \
   -H 'accept: application/json' \
   -H 'Content-Type: application/json' \
   -d '{
   "site_id": "SITEID1",
   "cpu": 8,
   "mem": 32,
   "storage": 1024
   }'
   curl -X 'POST' \
   'http://localhost:8000/nodes/' \
   -H 'accept: application/json' \
   -H 'Content-Type: application/json' \
   -d '{
   "site_id": "SITEID2",
   "cpu": 32,
   "mem": 128,
   "storage": 3072
   }'
   ```

   ```
   curl -X 'GET' \
  'http://localhost:8000/nodes/SITEID1' \
  -H 'accept: application/json'
  ```
<!-- uvicorn topology_server:app --reload -->

   <!-- Start SC + add demo functions from another window (4)

   ```
   git clone https://github.com/nubispc/desire6g-service-catalog
   cd desire6g-service-catalog
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app:app --reload --host 0.0.0.0 --port 8001
   curl -X POST -H "Content-Type: application/json" -d '{"name": "graph1", "data": {"nodes": ["A", "B"], "edges": ["A", "B"]}}' http://localhost:8001/store
   ``` -->
   <!-- uvicorn server:app --reload -->

1. Build the OE Docker image from another window (5):

   ```
   sudo docker build -f Dockerfile.msrv-prcr -t msrv-prcr .
   ```
2. Run the Docker container:
   SITE, specify the site id that the OE is running on (as a String: e.g. SITEID1).
   The rest as msrv-prcr, check the other README.md

   ```
   sudo docker run -it --rm --link rabbitmq:3-management -e RABBITMQ_HOST=3-management -e OUTPUT_TOPIC=myoutput -e INPUT_TOPIC=myinput -e SITE=SITEID1 msrv-prcr
   ```

3. Send a service request from window (1)
   ```
   python3 publish.py
   ```

4. Monitor the logs for processing information and errors from window (5).

## Folder Structure

<!-- - `processor.py`: Main script for the msrv-prcr service.
- `ProcessingSystems/`: Contains modules for processing messages.
- `requirements.txt`: Specifies the required Python packages.
- `Dockerfile.msrv-prcr`: Dockerfile for building the Docker image.
- `README.md`: This file. -->

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or features you'd like to add.

## License

[MIT License](LICENSE)
