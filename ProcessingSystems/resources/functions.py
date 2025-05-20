# Mock Demo2 Service Catalog for development
import time
import logging
import requests
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

network_functions = {
    "network-functions": [
        {
            "nf-instance-id": "flowcl-i01",
            "nf-instance-d6g-id": "101",
            "nf-id": "flowcl",
            "nf-name": "Flow Classifier",
            "nf-version": "v1.0",
            "nf-mgmt-network": "shared-mgmt-net",
            "nf-vcpu": 8,
            "nf-memory": 16,
            "nf-storage": 100
        },
        {
            "nf-instance-id": "firewall-i01",
            "nf-instance-d6g-id": "102",
            "nf-id": "firewall",
            "nf-name": "ACL Firewall",
            "nf-version": "v1.0",
            "nf-mgmt-network": "shared-mgmt-net",
            "nf-vcpu": 4,
            "nf-memory": 4,
            "nf-storage": 30
        }
    ]
}

application_functions = {
    "application-functions": [
        {
            "af-instance-id": "lws-i01",
            "af-instance-d6g-id": "103",
            "af-id": "localwebserver",
            "af-name": "Local web server for an example service",
            "af-version": "1.0",
            "af-mgmt-network": "shared-mgmt-net",
            "nf-vcpu": 2,
            "nf-memory": 8,
            "nf-storage": 30
        }
    ]
}

def fetchFunctions(data): 

    merged_functions = {
        **network_functions,
        **application_functions
    }

    return merged_functions

def call_service_catalog(graph_name = "graph1"):
    try:
        response = requests.get("http://localhost:8000/retrieve/{graph_id}")
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse YAML response into dictionary
        sc_graph = yaml.safe_load(response.text)
        logger.error(f"sc_graph received from SC -> {sc_graph}")
        return sc_graph
    except requests.RequestException as e:
        logger.error(f"Error making request to service catalog: {e}")
        return None
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML response: {e}")
        return None