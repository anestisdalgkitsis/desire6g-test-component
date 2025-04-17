# Python Modules
import json
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
    "partition.py": {"enabled": False},
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
        error_payload = {"Error": "Failed to fetch function information, check configuration."}
        return json.dumps(error_payload).encode('utf-8')
    else:
        logger.info("Function information fetched successfully from the Service Catalog module.")

    # Fetch topology (Simulate call to Topology)
    logger.info("Fetching topology from Topology module...")
    topologyGraph, domains, site_resources = topology.fetchTopology()
    logger.info("Domains" + str(domains))
    if topologyGraph is None:
        logger.info("Error: Failed to fetch topology, check configuration.")
        error_payload = {"Error": "Failed to fetch topology, check configuration."}
        return json.dumps(error_payload).encode('utf-8')
    else:
        logger.info("Topology fetched successfully from Topology module.")

    # Translate to internal structure
    logger.info("Translating service request to internal graph...")
    serviceGraph, decorations = translator.request2graph(data, function_info)
    if serviceGraph is None:
        logger.info("Error: Failed to translate service request, check syntax.")
        error_payload = {"Error": "Failed to translate service request, check syntax."}
        return json.dumps(error_payload).encode('utf-8')
    else:
        logger.info("Service request decoded successfully.")

    # Check for resource availability
    logger.info("Checking resource availability...")
    if check_resources(function_info, site_resources):
        logger.info("Ok: There are enough resources to host the service in the current region.")
    else:
        logger.info("Failed: The local region does not have enough resources to host the service.")
        error_payload = {"Failed": "The local region does not have enough resources to host the service. Relaying service request to the next region."}
        return json.dumps(error_payload).encode('utf-8')
    
    # Check if only one site, then relay the request to the site
    if domains == 1:
        return json.dumps(data).encode('utf-8')

    # Route to enabled autoselector (Randomized Demo) from Selector Pool
    pick = random_selection.spinwheel(algorithms)
    logger.info("Model Selector: " + str(pick))

    # Route to selected Model from Model Pool
    subgraphs = []
    try:
        if pick == "partition.py (Default)":
            subgraphs = partition.partition(serviceGraph, topologyGraph, domains)
        elif pick == "autologic.py":
            subgraphs = autologic.autologic(serviceGraph, topologyGraph, domains)
        elif pick == "greedysplit.py":
            subgraphs = greedysplit.greedysplit(serviceGraph, topologyGraph, domains)
        else:
            logger.info("Error: Unknown model selected, check Model Pool configuration.")
            error_payload = "Error: Unknown model selected, check Model Pool configuration."
            return json.dumps(error_payload).encode('utf-8')
    except Exception as e:
        logger.error("Internal error occurred in selected model: " + str(e))
        error_payload = {"Error": "Internal error occurred in selected model: " + str(e)}
        return json.dumps(error_payload).encode('utf-8')
    
    # Check if partitioning was successfull
    if subgraphs is None or subgraphs == []:
        logger.info("Error: Unknown partitioning error.")
    elif subgraphs == -1:
        logger.info("Service partitioning has failed, not enough resources to allocate.")
        # Then return the error
        error_payload = {"Failed": "Service partitioning has failed, not enough resources to allocate."}
        return json.dumps(error_payload).encode('utf-8')
    else:
        logger.info("Partitioning executed successfully. Count: " + str(len(subgraphs)) + " subgraphs: " + str(subgraphs))

    # Translate to YAML for SO
    encoded_subgraphs = []
    for subgraph in subgraphs:
        encoded_subgraph = translator.graph2request(subgraph, data)
        if encoded_subgraph is None:
            logger.info("Error: Failed to encode subgraph, check syntax: " + str(subgraph))
            error_payload = {"Error": "Failed to encode subgraph, check syntax: " + str(subgraph)}
            return json.dumps(error_payload).encode('utf-8')
        else:
            encoded_subgraphs.append(encoded_subgraph)
            logger.info("Subgraph encoded successfully.")
    logger.info("Combined subgraphs encoded successfully.")

    try:
        # Combine Response
        combined_response = []
        for domain in range(0, domains-1):
            combined_response.append({f"s{domain+1}e": encoded_subgraphs[domain], "site_id": f"SITEID{domain+1}"})
        logger.info("Combined response ready.")
    except Exception as e:
        logger.exception("An error occurred while combining the response: %s", e)
        error_payload = {"Error": "An error occurred while combining the response: " + str(e)}
        return json.dumps(error_payload).encode('utf-8')

    # Return Partitioned Request
    logger.info("Returning optimized service request.")
    # logger.info("-----")
    # logger.info(combined_response)
    # logger.info("-----")
    # return combined_response
    return json.dumps(combined_response).encode('utf-8')

def check_resources(merged_functions, site_resources):

    # Calculate total required resources from all functions.
    total_required_vcpu = 0
    total_required_ram = 0
    total_required_storage = 0

    for key, func_list in merged_functions.items():
        if not isinstance(func_list, list):
            logger.info("Warning: Expected %s to be a list, got %s. Skipping.", key, type(func_list))
            continue
        for func in func_list:
            if not isinstance(func, dict):
                logger.info("Warning: Expected function info to be dict, got %s. Skipping: %s", type(func), func)
                continue
            total_required_vcpu += int(func.get("nf-vcpu", 0))
            total_required_ram += int(func.get("nf-memory", 0))
            total_required_storage += int(func.get("nf-storage", 0))

    # Calculate total available resources from site resources.
    total_available_vcpu = 0
    total_available_ram = 0
    total_available_storage = 0

    site_resources_list = site_resources.get("site-resources", [])
    for site in site_resources_list:
        if not isinstance(site, dict):
            # Log error and skip if the item is not a dictionary.
            logger.error("Expected site to be a dictionary but got %s: %s", type(site), site)
            continue
        total_available_vcpu += int(site.get("site-available-vcpu", 0))
        total_available_ram += int(site.get("site-available-ram", 0))
        total_available_storage += int(site.get("site-available-storage", 0))

    logger.info("Total required vCPU: %s", total_required_vcpu)
    logger.info("Total available vCPU: %s", total_available_vcpu)
    logger.info("Total required RAM: %s", total_required_ram)
    logger.info("Total available RAM: %s", total_available_ram)
    logger.info("Total required Storage: %s", total_required_storage)
    logger.info("Total available Storage: %s", total_available_storage)

    # Check if available resources cover the required resources.
    if (total_required_vcpu <= total_available_vcpu and
        total_required_ram <= total_available_ram and
        total_required_storage <= total_available_storage):
        return True
    else:
        return False