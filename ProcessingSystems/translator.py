# Two-way JSON/YAML to NetworkX translation
# Port from Dr. Anestis Dalgkitsis work
# v2.1

import networkx as nx
import yaml
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def request2graph(service):
    """
    Constructs an undirected networkx graph based on the "forwarding_graphs" section
    of the service. The nodes of the graph are taken from the "network-functions" and 
    "application-functions" sections. All other information is stored in the 
    "decorations" dictionary which is returned alongside the graph.
    
    Parameters:
        service (dict): The input service dictionary.
        
    Returns:
        tuple: A tuple containing the constructed networkx.Graph and a dictionary of decorations.
    """
    try:
        # If the service is a bytes object, decode it to a string and then parse as JSON.
        if isinstance(service, bytes):
            service = json.loads(service.decode('utf-8'))
        
        # If the service is wrapped under a key (like "local-nsd"), extract it.
        nsd = service.get("local-nsd", service)
        
        # Create an empty undirected graph.
        G = nx.Graph()
        
        # Extract nodes from network-functions and application-functions.
        network_functions = nsd.get("network-functions", [])
        application_functions = nsd.get("application-functions", [])
        
        # Add network function nodes.
        for nf in network_functions:
            node_id = nf.get("nf-instance-id")
            if node_id:
                G.add_node(node_id, **nf)
            else:
                logger.info("Network function missing 'nf-instance-id': %s", nf)
        
        # Add application function nodes.
        for af in application_functions:
            node_id = af.get("af-instance-id")
            if node_id:
                G.add_node(node_id, **af)
            else:
                logger.info("Application function missing 'af-instance-id': %s", af)
        
        # Process forwarding_graphs to add edges between nodes.
        forwarding_graphs = nsd.get("forwarding_graphs", [])
        for fg in forwarding_graphs:
            links = fg.get("links", [])
            for link in links:
                connection_points = link.get("connection-points", [])
                if len(connection_points) < 2:
                    logger.info("Link '%s' has less than 2 connection points.", link.get("link-id", "unknown"))
                    continue
                # Extract the first two connection points.
                cp1 = connection_points[0]
                cp2 = connection_points[1]
                # Extract node identifiers by splitting on ':'.
                ref1 = cp1.get("member-if-id-ref", "")
                ref2 = cp2.get("member-if-id-ref", "")
                node1_id = ref1.split(":")[0] if ref1 else None
                node2_id = ref2.split(":")[0] if ref2 else None
                
                # Check if both nodes exist in the graph before adding the edge.
                if node1_id in G.nodes and node2_id in G.nodes:
                    G.add_edge(node1_id, node2_id, link_id=link.get("link-id"))
                else:
                    logger.info("Skipping edge for link '%s': Node '%s' or '%s' not found in functions.", link.get("link-id", "unknown"), node1_id, node2_id)
        
        # Store the rest of the information as decorations.
        decorations = {key: value for key, value in nsd.items() if key not in ["network-functions", "application-functions", "forwarding_graphs"]}

        return G, decorations
    
    except Exception as e:
        logger.info("Error in request2graph: %s", e)
        return None, None
    
def graph2request(graph, data={}):
    """
    Constructs a service request dictionary adhering to the local_nsd_v2.yml schema 
    from a networkx graph and additional data (decorations).

    Parameters:
        graph (networkx.Graph): The graph representing network and application functions.
        data (dict): Additional service decorations and configuration parameters.

    Returns:
        dict: A dictionary conforming to the local_nsd_v2.yml structure describing a network service.
    """
    try:
        # Initialize the service with provided data under the "local-nsd" key.
        # If data is already structured with "local-nsd", we use it directly.
        if "local-nsd" in data:
            service = data.copy()
        else:
            service = {"local-nsd": {}}
            service["local-nsd"].update(data)

        nsd = service["local-nsd"]

        # Initialize lists for network-functions and application-functions.
        nsd["network-functions"] = []
        nsd["application-functions"] = []

        # Process each node in the graph.
        for node, attrs in graph.nodes(data=True):
            if "nf-instance-id" in attrs:
                # Append the full attribute dict for network functions.
                nsd["network-functions"].append(attrs)
            elif "af-instance-id" in attrs:
                # Append the full attribute dict for application functions.
                nsd["application-functions"].append(attrs)
            else:
                logger.info("Node '%s' does not have a valid function identifier.", node)

        # Process graph edges into a single forwarding graph.
        links = []
        for u, v, edge_attrs in graph.edges(data=True):
            # Use the provided link_id or generate a default one.
            link_id = edge_attrs.get("link_id", f"{u}-{v}")
            # Build a link with two connection points.
            link = {
                "link-id": link_id,
                "connection-points": [
                    {"member-connection-point-index": 1, "member-if-id-ref": u},
                    {"member-connection-point-index": 2, "member-if-id-ref": v}
                ]
            }
            links.append(link)

        # Create a default forwarding graph segment.
        nsd["forwarding_graphs"] = [{
            "member-graph-index": 1,
            "graph-name": "default",
            "links": links,
            "site-delay-budget": "0ms"
        }]

        return service

    except Exception as e:
        logger.info("Error in graph2request: %s", e)
        return None

