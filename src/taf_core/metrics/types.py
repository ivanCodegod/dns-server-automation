from dataclasses import dataclass


@dataclass
class PageLoadMetrics:
    total_requests: int
    dom_load_time_ms: float = 0
    page_load_time_ms: float = 0

    def __str__(self):
        return (
            f"| Total Requests | DOM Load (ms) | Page Load (ms) |\n"
            f"| {self.total_requests:^14} | {self.dom_load_time_ms:^13} | {self.page_load_time_ms:^14} |"
        )
