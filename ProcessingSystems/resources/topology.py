# Mock Demo2 Topology for development
import networkx as nx
import requests
import logging
import numpy

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
            "site-id-ref": "d6g-002",
            "site-available-vcpu": 2,
            "site-available-ram": 1,
            "site-available-storage": 3072
        }
        # ,
        # {
        #     "site-id-ref": "d6g-003-adam",
        #     "site-available-vcpu": 32,
        #     "site-available-ram": 128,
        #     "site-available-storage": 3072
        # },
        # {
        #     "site-id-ref": "d6g-004",
        #     "site-available-vcpu": 1,
        #     "site-available-ram": 16
        # }
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

    for domain in site_resources["site-resources"]:
        sites += 1

    # time.sleep(1.8) # Slow down the process for demo purposes

    return G, sites, site_resources

def fetch_d6g_site_info(d6g_site):

    url = f"http://localhost:8000/nodes/{d6g_site}"
    headers = {"Accept": "application/json"}

    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()          # error on 
        site_json = resp.json()          # parse JSON into dict
        return site_json
    except requests.RequestException as e:
        logger.error(f"HTTP error fetching node from Topology Module'{d6g_site}': {e}")
    except ValueError as e:
        logger.error(f"Error parsing JSON from Topology Module for '{d6g_site}': {e}")
    return None
