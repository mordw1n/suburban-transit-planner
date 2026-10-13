import time
import logging
from enum import Enum
from app.config import settings

logger = logging.getLogger("transit.circuit_breaker")

class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreaker:
    def __init__(self, fail_max: int = 5, reset_timeout: int = 60):
        self.fail_max = fail_max
        self.reset_timeout = reset_timeout
        self.state = CircuitState.CLOSED
        self.fail_count = 0
        self.last_state_change = time.time()

    def record_success(self):
        if self.state != CircuitState.CLOSED:
            logger.info(f"Circuit Breaker recovered: {self.state} -> CLOSED")
        self.state = CircuitState.CLOSED
        self.fail_count = 0
        self.last_state_change = time.time()

    def record_failure(self):
        self.fail_count += 1
        logger.warning(f"Failure count: {self.fail_count}/{self.fail_max}")
        if self.fail_count >= self.fail_max and self.state != CircuitState.OPEN:
            self.state = CircuitState.OPEN
            self.last_state_change = time.time()
            logger.error(f"Circuit Breaker tripped to OPEN, timeout: {self.reset_timeout}s")

    def can_execute(self) -> bool:
        now = time.time()
        if self.state == CircuitState.OPEN:
            if now - self.last_state_change > self.reset_timeout:
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = now
                logger.info("Circuit Breaker transitioned to HALF_OPEN")
                return True
            return False
        return True

    def is_degraded(self) -> bool:
        return self.state in [CircuitState.OPEN, CircuitState.HALF_OPEN]

yandex_breaker = CircuitBreaker(
    fail_max=settings.CIRCUIT_BREAKER_FAIL_MAX,
    reset_timeout=settings.CIRCUIT_BREAKER_RESET_TIMEOUT
)
