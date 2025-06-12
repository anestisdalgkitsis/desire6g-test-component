# Mock Demo2 Topology for development
import networkx as nx
import requests
import logging
import numpy
import subprocess
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

site_connections = {
    "site-connections": [
        {
            "site-connection-id": "sc1-sc2",
            "site-id-ref": "d6g-002",
            "site-available-vcpu": 2,
            "site-available-ram": 1,
            "tunnel-id": "444"
        },
        # {
        #     "site-connection-id": "sc1-sc3",
        #     "site-id-ref": "d6g-003",
        #     "site-available-vcpu": "8",
        #     "site-available-ram": "48",
        #     "tunnel-id": "321",
        # },
        {
            "site-connection-id": "sc1-sc3",
            "site-id-ref": "d6g-003-adam",
            "site-available-vcpu": 32,
            "site-available-ram": 128,
            "site-available-storage": 3072,
            "tunnel-id": "321"
        },
        {
            "site-connection-id": "sc1-sc4",
            "site-id-ref": "d6g-004",
            "site-available-vcpu": 1,
            "site-available-ram": 16,
            "tunnel-id": "123"
        }
    ]
}

site_resources = {
    "site-resources": [
        {
            "site-id-ref": "SITEID1",
            "site-available-vcpu": 2,
            "site-available-ram": 1,
            "site-available-storage": 3072
        }
    ]
}

site_resources2 = {
    "site-resources": [
        {
            "site-id-ref": "SITEID2",
            "site-available-vcpu": 32,
            "site-available-ram": 128,
            "site-available-storage": 3072
        },
    ]
}

def fetchTopology(d6g_site):

    logger.info("Fetching topology for site: " + d6g_site)

    # Create topology graph
    G = nx.Graph()

    sites = 0

    # Add nodes and edges from the site connections
    for connection in site_connections["site-connections"]:
        site_id = connection["site-id-ref"]
        vcpu = int(connection["site-available-vcpu"])
        ram = int(connection["site-available-ram"])
        
        # Add site nodes with attributes
        if site_id not in G:
            G.add_node(site_id, vcpu=vcpu, ram=ram)

        # Add edges (connections) between nodes
        G.add_edge("sc1", site_id, tunnel_id=connection["tunnel-id"])

        # # Add site
        # sites += 1

    if d6g_site == "SITEID1":
        site_data = site_resources["site-resources"][0]
        cpu = site_data["site-available-vcpu"]
        mem = site_data["site-available-ram"]
        storage = site_data["site-available-storage"]
    elif d6g_site == "SITEID2":
        site_data = site_resources2["site-resources"][0]
        cpu = site_data["site-available-vcpu"]
        mem = site_data["site-available-ram"]
        storage = site_data["site-available-storage"]
    else:
        logger.info("Error: Invalid site ID")
        return None, None, None

    # time.sleep(1.8) # Slow down the process for demo purposes

    return G, 1, site_data

def fetch_d6g_site_info(d6g_site):
    """
    Get site information using requests to match the curl command behavior.
    Returns a dictionary with cpu, mem, and storage values.
    """
    try:
        # Use requests to make the same GET request as curl
        url = f'http://localhost:8000/nodes/{d6g_site}'
        headers = {'accept': 'application/json'}
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the JSON response
        site_info = response.json()
        
        # Store the values in a dictionary
        site_data = {
            'cpu': site_info.get('cpu', 0),
            'mem': site_info.get('mem', 0),
            'storage': site_info.get('storage', 0)
        }
        
        logger.info(f"Successfully retrieved site info for {d6g_site}: {site_data}")
        return site_data
        
    except requests.RequestException as e:
        logger.error(f"Error making request for site {d6g_site}: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON response for site {d6g_site}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting site info for {d6g_site}: {e}")
        return None