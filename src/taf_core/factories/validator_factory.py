from src.taf_core.metrics.network_manager import NetworkMetricsManager
from src.taf_core.validators.network_metrics_validator import NetworkMetricsValidator


def create_network_metrics_validator(metrics_mgr: NetworkMetricsManager) -> NetworkMetricsValidator:
    return NetworkMetricsValidator(metrics_mgr)
