# Mock Infrastructure Monitoring for development
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def monitor_resources():
    pass

def monitor_performance():
    pass

def monitor_availability():
    pass

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