# Optimization Engine Desire6G Module

Based on Message Processor Application by NUBIS (msrv-prcr).

<!-- ## Description

TODO

## Overview

TODO -->

## 5TONIC INTEGRATION STEPS (FOR NUBIS)

These steps assume the following, update accordingly

1. Add the two Desire6G Sites to the Topology Module (TM), assuming that the TM is available at localhost with port 8000:

   ```bash
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

2. Add functions to the Service Catalog (SC), assuming that the SC is available at localhost with port 8003:

   ```bash
   curl -X POST -H "Content-Type: application/json" -d '{"name": "apps","data": {"network-functions": [{"nf-instance-id": "flowcl-i01", "nf-vcpu": 8, "nf-memory": 16, "nf-storage": 100}, {"nf-instance-id": "firewall-i01", "nf-vcpu": 4, "nf-memory": 4, "nf-storage": 30}], "application-functions": [{"af-instance-id": "lws-i01", "nf-vcpu": 2, "nf-memory": 8, "nf-storage": 30}]}}' http://localhost:8003/store
   ```
3. Build the OE container at the project root folder:

   ```bash
   sudo docker build -f Dockerfile.msrv-prcr -t msrv-prcr .
   ```

4. Instantiate the OE as follows, adjust the arguments accordingly:

   ```bash
   sudo docker run -it --rm --link rabbitmq:3-management -e RABBITMQ_HOST=3-management -e OUTPUT_TOPIC=myoutput -e INPUT_TOPIC=myinput -e SITE=SITEID1 -e TOPOLOGY_MODULE_HOST=localhost -e TOPOLOGY_MODULE_PORT=8000 -e SERVICE_CATALOG_HOST=localhost -e SERVICE_CATALOG_PORT=8003 msrv-prcr
   ```

   Arguments (pay attention to the SO RabbitMQ topics):
   - rabbitmq: link RabbitMQ Server 
   - RABBITMQ_HOST: RabbitMQ Host name
   - OUTPUT_TOPIC: RabbitMQ Topic that SO will RECEIVE the optimized services.
   - INPUT_TOPIC: RabbitMQ Topic that SO will SEND the service requests for optimization.
   - SITE: D6G Site ID where the OE is located (can be SITEID1 or SITEID2, used to fetch topology)
   - TOPOLOGY_MODULE_HOST: Hostname for the Topology Module
   - TOPOLOGY_MODULE_PORT: Port number for the Topology Module
   - SERVICE_CATALOG_HOST: Hostname for the Service Catalog
   - SERVICE_CATALOG_PORT: Port number for the Service Catalog
   

5. Send the "demo_nsd.sg.yml" request from the SO to the OE for optimization.

## DESIRE6G Live DEMO2 Behavior (Expected outputs)

If the Optimization Engine is instantiated in SITEID1, according to the pre-determined demo workflow, the response to the SO topic should be an error stating lack of resources, as follows:

```
{'Failed': 'The local region does not have enough resources to host the service. Relaying service request to the next region.'}
```

If the Optimization Engine is instantiated in SITEID2, it should log success and forward the original service request, as there is only one internal domain node and there is no need for partitioning:

```
{"local-nsd": {"info": {"ns-instance-id": "1", "description": "Example ... }}}
```

## Local Demo Testing Environment Instructions (Docker Desktop)

1. Start a RabbitMQ server:

   ```
   docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
   ```

   Open a window (1) to send the request (simulate the SO and IBN functionality).
   You will need the "demo_nsd.sg.yml" in this folder, edit the "publish.py" file to send it accordingly.

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

2. Start Topology + add demo SITEID1 and SITEID2 from another window (3)

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

   (Optional) Check if the Topology API works:

   ```
   curl -X 'GET' \
   'http://localhost:8000/nodes/SITEID1' \
   -H 'accept: application/json'
   ```

3. Start Service Catalog + add Demo functions to be fetched

   ```
   git clone https://github.com/nubispc/desire6g-service-catalog
   cd desire6g-service-catalog
   python3 -m venv venv
   source venv/bin/activate
   pip install fastapi uvicorn
   pip install -r requirements.txt
   uvicorn app:app --reload --host 0.0.0.0 --port 8003
   curl -X POST -H "Content-Type: application/json" -d '{"name": "apps","data": {"network-functions": [{"nf-instance-id": "flowcl-i01", "nf-vcpu": 8, "nf-memory": 16, "nf-storage": 100}, {"nf-instance-id": "firewall-i01", "nf-vcpu": 4, "nf-memory": 4, "nf-storage": 30}], "application-functions": [{"af-instance-id": "lws-i01", "nf-vcpu": 2, "nf-memory": 8, "nf-storage": 30}]}}' http://localhost:8003/store
   ```

   (Optional) Check if the SC API works:

   ```
   curl http://localhost:8003/retrieve/apps
   ```
4. Build the OE Docker image from another window (5):

   ```
   sudo docker build -f Dockerfile.msrv-prcr -t msrv-prcr .
   ```
5. Run the Docker container:
   SITE, specify the site id that the OE is running on (as a String: e.g. SITEID1).
   The rest as msrv-prcr, check the other README.md

   ```
   sudo docker run -it --rm --link rabbitmq:3-management -e RABBITMQ_HOST=3-management -e OUTPUT_TOPIC=myoutput -e INPUT_TOPIC=myinput -e SITE=SITEID1 -e TOPOLOGY_MODULE_HOST=host.docker.internal -e TOPOLOGY_MODULE_PORT=8000 -e SERVICE_CATALOG_HOST=host.docker.internal -e SERVICE_CATALOG_PORT=8003 msrv-prcr
   ```
5. Send a service request from window (1)

   ```
   python3 publish.py
   ```
7. Monitor the logs for processing information and errors from window (5).

## Live Behavior (non Desire6G Demo)

If the Optimization Engine is instantiated in a site with more than one node and enough resources to host the service, a random partitioning algorithm from the model pool to perform a mock partitioning. The module will return a list with the partitioned subgraphs:

```
{"s0e": { ... } }{"s1e": { ... } } ...
```

<!-- ## Folder Structure

- `processor.py`: Main script for the msrv-prcr service.
- `ProcessingSystems/`: Contains modules for processing messages.
- `requirements.txt`: Specifies the required Python packages.
- `Dockerfile.msrv-prcr`: Dockerfile for building the Docker image.
- `README.md`: This file. -->

## Toubleshooting

### X module not reachable.

Use host.docker.internal istead of local when the modules are instantiated locally, but the OE is running in a container.

## Maintenance

The repository mainentance will end together with the DESIRE6G EU project.

## License

[MIT License](LICENSE)
