# Mock Demo2 Topology for development
import networkx as nx
import numpy
import time

site_connections = {
    "site-connections": [
        {
            "site-connection-id": "sc1-sc2",
            "site-id-ref": "d6g-002",
            "site-available-vcpu": "2", # Added for OE
            "site-available-ram": "1", # Added for OE
            "tunnel-id": "444",
        },
        {
            "site-connection-id": "sc1-sc3",
            "site-id-ref": "d6g-003",
            "site-available-vcpu": "8", # Added for OE
            "site-available-ram": "48", # Added for OE
            "tunnel-id": "321",
        },
        {
            "site-connection-id": "sc1-sc4",
            "site-id-ref": "d6g-004",
            "site-available-vcpu": "1", # Added for OE
            "site-available-ram": "16", # Added for OE
            "tunnel-id": "123",
        },
    ]
}

def fetchTopology():

    # Create an empty graph
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

        # Add site
        sites += 1

    time.sleep(1.8) # Slow down the process for demo purposes

    return G, sites
