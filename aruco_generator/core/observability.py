"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>observability.py</name>
    <version>1.0.0</version>
    <type>core_observability_module</type>
    <purpose>Request tracing, error heuristics, and health metrics aggregation</purpose>
    <last_updated>2026-02-07</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>
</ai_agent_documentation>
-->
"""

from __future__ import annotations

import logging
import time
import uuid
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, Optional, Tuple

from flask import g, request

logger = logging.getLogger(__name__)


@dataclass
class ObservabilityConfig:
    """Configuration for request metrics and heuristics."""

    window_seconds: int = 300
    min_requests: int = 20
    error_rate_warn: float = 0.1
    slow_request_ms: int = 2000
    warn_cooldown_seconds: int = 60


class RequestMetrics:
    """Track recent request outcomes for health and logging heuristics."""

    def __init__(self, config: ObservabilityConfig) -> None:
        self.config = config
        self.samples: Deque[Tuple[float, int, float]] = deque()
        self._last_warning_ts = 0.0

    def record(self, status_code: int, duration_ms: float) -> None:
        now = time.time()
        self.samples.append((now, status_code, duration_ms))
        self._trim(now)

    def snapshot(self) -> Dict[str, float | int]:
        now = time.time()
        self._trim(now)
        total = len(self.samples)
        errors_5xx = sum(1 for _, status, _ in self.samples if status >= 500)
        errors_4xx = sum(1 for _, status, _ in self.samples if 400 <= status < 500)
        durations = [duration for _, _, duration in self.samples]
        avg_ms = sum(durations) / total if total else 0.0
        p95_ms = self._percentile(durations, 0.95)
        slow_count = sum(1 for d in durations if d >= self.config.slow_request_ms)
        error_rate = (errors_5xx / total) if total else 0.0
        client_error_rate = (errors_4xx / total) if total else 0.0

        return {
            "window_seconds": self.config.window_seconds,
            "total_requests": total,
            "errors_5xx": errors_5xx,
            "errors_4xx": errors_4xx,
            "error_rate_5xx": round(error_rate, 4),
            "error_rate_4xx": round(client_error_rate, 4),
            "avg_ms": round(avg_ms, 2),
            "p95_ms": round(p95_ms, 2),
            "slow_threshold_ms": self.config.slow_request_ms,
            "slow_requests": slow_count,
        }

    def maybe_warn(self) -> None:
        now = time.time()
        if now - self._last_warning_ts < self.config.warn_cooldown_seconds:
            return

        snapshot = self.snapshot()
        total = snapshot["total_requests"]
        error_rate = snapshot["error_rate_5xx"]
        if (
            total >= self.config.min_requests
            and error_rate >= self.config.error_rate_warn
        ):
            self._last_warning_ts = now
            logger.warning(
                "High API error rate detected | total=%s error_rate_5xx=%s window=%ss",
                total,
                error_rate,
                self.config.window_seconds,
            )

    def _trim(self, now: Optional[float] = None) -> None:
        if now is None:
            now = time.time()
        cutoff = now - self.config.window_seconds
        while self.samples and self.samples[0][0] < cutoff:
            self.samples.popleft()

    @staticmethod
    def _percentile(values: list[float], quantile: float) -> float:
        if not values:
            return 0.0
        values_sorted = sorted(values)
        index = int(round((len(values_sorted) - 1) * quantile))
        return values_sorted[min(max(index, 0), len(values_sorted) - 1)]


def init_observability(app) -> None:
    """Attach request tracing and logging heuristics to the Flask app."""

    config = ObservabilityConfig(
        window_seconds=app.config.get("METRICS_WINDOW_SECONDS", 300),
        min_requests=app.config.get("ERROR_RATE_MIN_REQUESTS", 20),
        error_rate_warn=app.config.get("ERROR_RATE_WARN_THRESHOLD", 0.1),
        slow_request_ms=app.config.get("SLOW_REQUEST_MS", 2000),
        warn_cooldown_seconds=app.config.get("ERROR_RATE_WARN_COOLDOWN", 60),
    )
    metrics = RequestMetrics(config)
    app.extensions["request_metrics"] = metrics
    app.config.setdefault("APP_START_TIME", time.time())

    @app.before_request
    def _start_request() -> None:
        g.request_start_time = time.monotonic()
        client_request_id = request.headers.get("X-Request-Id")
        g.client_request_id = client_request_id
        g.request_id = client_request_id or uuid.uuid4().hex

    @app.after_request
    def _after_request(response):
        duration_ms = (time.monotonic() - g.request_start_time) * 1000
        response.headers["X-Request-Id"] = g.request_id
        response.headers["X-Response-Time-ms"] = f"{duration_ms:.2f}"

        metrics.record(response.status_code, duration_ms)
        metrics.maybe_warn()

        if request.path.startswith("/api/"):
            log_level = logging.INFO
            if response.status_code >= 500:
                log_level = logging.ERROR
            elif response.status_code >= 400:
                log_level = logging.WARNING
            elif duration_ms >= config.slow_request_ms:
                log_level = logging.WARNING

            logger.log(
                log_level,
                "api_request %s %s status=%s duration_ms=%.2f request_id=%s client_request_id=%s",
                request.method,
                request.path,
                response.status_code,
                duration_ms,
                g.request_id,
                g.client_request_id,
            )

        return response

    @app.teardown_request
    def _teardown_request(error) -> None:
        if error is not None:
            logger.error(
                "request_teardown_error path=%s request_id=%s",
                request.path,
                getattr(g, "request_id", "unknown"),
                exc_info=error,
            )


def get_metrics_snapshot(app) -> Dict[str, float | int]:
    """Return a snapshot of recent request metrics."""
    metrics: Optional[RequestMetrics] = app.extensions.get("request_metrics")
    if not metrics:
        return {
            "window_seconds": 0,
            "total_requests": 0,
            "errors_5xx": 0,
            "errors_4xx": 0,
            "error_rate_5xx": 0.0,
            "error_rate_4xx": 0.0,
            "avg_ms": 0.0,
            "p95_ms": 0.0,
            "slow_threshold_ms": 0,
            "slow_requests": 0,
        }
    return metrics.snapshot()
