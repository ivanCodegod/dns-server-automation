import logging

from src.taf_core.factories.dns_fetcher_factory import create_dns_fetcher


logger = logging.getLogger(__name__)


def get_dns_servers() -> list[str]:
    dns_servers = create_dns_fetcher().get_dns_servers()
    if dns_servers:
        logger.info("Current DNS servers: %s", dns_servers)
    else:
        logger.warning("No DNS servers found.")
