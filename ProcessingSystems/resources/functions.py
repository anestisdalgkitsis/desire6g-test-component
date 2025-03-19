# Mock Demo2 Service Catalog for development
import time
import logging

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

    time.sleep(1.2) # Slow down the process for demo purposes

    return merged_functions
