# Python Modules
import logging

# Local Modules
import ProcessingSystems.translator as translator

# Demo Selector Pool
import ProcessingSystems.selector_pool.random_selection as random_selection

# Demo Model Pool
import ProcessingSystems.model_pool.partition as partition
import ProcessingSystems.model_pool.autologic as autologic
import ProcessingSystems.model_pool.greedysplit as greedysplit

# Demo Data
import ProcessingSystems.resources.topology as topology
import ProcessingSystems.resources.functions as functions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model Pool Demo Configuration
algorithms = {
    "partition.py (Default)": {"enabled": True},
    "autologic.py": {"enabled": True},
    "greedysplit.py": {"enabled": True},
}

# Model Selector Demo Configuration
selectors = {
    "spinwheel.py (Default)": {"enabled": True},
    "intelligence.py": {"enabled": False},
}

def optimization_engine(data):

    # Fetch VNF data (Simulate call to Service Catalog)
    logger.info("Fetching functions information from the Service Catalog module...")
    function_info = functions.fetchFunctions(data)
    if function_info is None:
        logger.info("Error: Failed to fetch function information, check configuration.")
        return -1
    else:
        logger.info("Function information fetched successfully from the Service Catalog module.")

    # Fetch topology (Simulate call to Topology)
    logger.info("Fetching topology from Topology module...")
    topologyGraph, domains = topology.fetchTopology()
    if topologyGraph is None:
        logger.info("Error: Failed to fetch topology, check configuration.")
        return -1
    else:
        logger.info("Topology fetched successfully from Topology module.")

    # Translate to internal structure
    logger.info("Translating service request to internal graph...")
    serviceGraph, decorations = translator.request2graph(data)
    if serviceGraph is None:
        logger.info("Error: Failed to translate service request, check syntax.")
        return -1
    else:
        logger.info("Service request decoded successfully.")

    # Route to enabled autoselector (Randomized Demo) from Selector Pool
    pick = random_selection.spinwheel(algorithms)
    logger.info("Model Selector: " + str(pick))

    # Route to selected Model from Model Pool
    subgraphs = []
    if pick == "partition.py (Default)":
        subgraphs = partition.partition(serviceGraph, topologyGraph, domains)
    elif pick == "autologic.py":
        subgraphs = autologic.autologic(serviceGraph, topologyGraph, domains)
    elif pick == "greedysplit.py":
        subgraphs = greedysplit.greedysplit(serviceGraph, topologyGraph, domains)
    else:
        logger.info("Error: Unknown model selected, check Model Pool configuration.")
        return -1
    
    # Check if partitioning was successfull
    # if subgraphs == None:
    if subgraphs is None or subgraphs == []:
        logger.info("Error: Unknown partitioning error.")
    elif subgraphs == -1:
        logger.info("Service partitioning has failed, not enough resources to allocate.")
        # Then return the error
        return "Service partitioning has failed, not enough resources to allocate."
        return -1
    else:
        logger.info("Partitioning executed successfully. Count: " + str(len(subgraphs)) + " subgraphs: " + str(subgraphs))

    # Translate to YAML for SO
    encoded_subgraphs = []
    for subgraph in subgraphs:
        encoded_subgraph = translator.graph2request(subgraph, data)
        if encoded_subgraph is None:
            logger.info("Error: Failed to encode subgraph, check syntax: " + str(subgraph))
            return -1
        else:
            encoded_subgraphs.append(encoded_subgraph)
            logger.info("Subgraph encoded successfully.")
    logger.info("Combined subgraphs encoded successfully.")

    # Combine Response
    combined_response = []
    for domain in domains:
        combined_response.append({f"s{domain+1}e": encoded_subgraphs[domain],"site_id": f"SITEID{domain+1}"})
    logger.info("Combined response ready.")

    # Return Partitioned Request
    logger.info("Returning optimized service request.")
    return combined_response