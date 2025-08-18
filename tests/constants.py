from enum import StrEnum


class CaseUrl(StrEnum):
    NETWORK = ""  # TODO: Add actual URL for the Network test suite


class Website(StrEnum):
    GOOGLE = "https://google.com"  # Popular Global Website
    ONET = "https://www.onet.pl"  # Content-heavy News Site
    EXAMPLE = "https://example.com"  # Less Popular / Random Domains
