import logging
import platform
import subprocess

from pathlib import Path


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

SYSTEM_NAME: str = platform.system().lower()


class DNSServerFetcher:
    """
    Utility class to fetch DNS servers depending on the operating system.

    This is useful in scenarios such as:
      - Debugging DNS resolution issues in automated tests.
      - Collecting system network configuration for monitoring or diagnostics.
      - Ensuring test environments (e.g., Docker containers, CI pipelines) are using
        the expected DNS servers.
      - Cross-platform tools that need to verify or adapt to system DNS settings.
    """

    @staticmethod
    def get_dns_servers() -> list[str]:
        """
        Return a list of DNS servers configured on the current system.
        Supports Linux, macOS, and provides extensibility for Windows or others.

        Returns:
            list[str]: A list of DNS server IP addresses.
        """
        try:
            if SYSTEM_NAME == "linux":
                return DNSServerFetcher._get_linux_dns()
            if SYSTEM_NAME == "darwin":
                return DNSServerFetcher._get_macos_dns()

            logger.warning("Unsupported operating system: %s", SYSTEM_NAME)
        except Exception:
            logger.exception("Error while fetching DNS servers")
        else:
            return []

    @staticmethod
    def _get_linux_dns() -> list[str]:
        """Fetch DNS servers from /etc/resolv.conf on Linux."""
        resolv_conf = Path("/etc/resolv.conf")
        servers: list[str] = []

        if resolv_conf.exists():
            with resolv_conf.open(encoding="utf-8") as file:
                for line in file:
                    dns_data = DNSServerFetcher._parse_dns_line(line)
                    if dns_data:
                        servers.append(dns_data)
        return servers

    @staticmethod
    def _get_macos_dns() -> list[str]:
        """
        Fetch DNS servers on macOS.
        First tries /etc/resolv.conf, then falls back to scutil.
        """
        servers = DNSServerFetcher._get_linux_dns()
        if servers:
            return servers

        result = subprocess.check_output(["scutil", "--dns"], text=True)
        for line in result.splitlines():
            dns_data = DNSServerFetcher._parse_dns_line(line)

            if dns_data:
                servers.append(dns_data)
        return servers

    @staticmethod
    def _get_windows_dns() -> list[str]:
        """Fetch DNS servers on Windows using ipconfig."""
        # TODO: Implement Windows DNS fetching logic; Use 'ipconfig /all' command

    @staticmethod
    def _parse_dns_line(line: str) -> str | None:
        """
        Extract DNS IP from a line, if present.
        Returns None if line does not contain a valid IP.
        """
        if line.startswith("nameserver"):
            return line.split()[-1]
        return None


if __name__ == "__main__":
    dns_servers = DNSServerFetcher.get_dns_servers()
    if dns_servers:
        logger.info("Current DNS servers: %s", dns_servers)
    else:
        logger.warning("No DNS servers found.")
