import time
import pytest
from app.circuit_breaker import CircuitBreaker, CircuitState

class TestCircuitBreaker:
    """Модульные тесты автомата состояний Circuit Breaker (Паттерн отказоустойчивости)."""

    def test_initial_state_closed(self):
        """В исходном состоянии автомат находится в CLOSED и разрешает вызовы."""
        cb = CircuitBreaker(fail_max=3, reset_timeout=30)
        assert cb.state == CircuitState.CLOSED
        assert cb.fail_count == 0
        assert cb.can_execute() is True
        assert cb.is_degraded() is False

    def test_success_resets_failure_count(self):
        """Успешный вызов обнуляет счетчик накопленных ошибок."""
        cb = CircuitBreaker(fail_max=3, reset_timeout=30)
        cb.record_failure()
        cb.record_failure()
        assert cb.fail_count == 2
        assert cb.state == CircuitState.CLOSED

        cb.record_success()
        assert cb.fail_count == 0
        assert cb.state == CircuitState.CLOSED

    def test_trips_to_open_after_max_failures(self):
        """При достижении fail_max автомат переходит в состояние OPEN."""
        cb = CircuitBreaker(fail_max=3, reset_timeout=30)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED

        cb.record_failure()  # Достигнут предел 3
        assert cb.state == CircuitState.OPEN
        assert cb.is_degraded() is True
        assert cb.can_execute() is False

    def test_blocks_calls_while_open(self):
        """В состоянии OPEN вызовы немедленно блокируются без сетевой нагрузки."""
        cb = CircuitBreaker(fail_max=2, reset_timeout=30)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

        # can_execute должен возвращать False до истечения таймаута
        assert cb.can_execute() is False

    def test_transitions_to_half_open_after_timeout(self):
        """По истечении reset_timeout автомат переходит в пробное состояние HALF_OPEN."""
        cb = CircuitBreaker(fail_max=2, reset_timeout=5)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

        # Симулируем прошествие времени (сдвиг метки времени изменения состояния)
        cb.last_state_change = time.time() - 6.0

        # Следующий вызов должен перевести в HALF_OPEN и разрешить 1 пробный запрос
        assert cb.can_execute() is True
        assert cb.state == CircuitState.HALF_OPEN
        assert cb.is_degraded() is True

    def test_half_open_recovers_to_closed_on_success(self):
        """Успешный пробный запрос в HALF_OPEN переводит автомат обратно в CLOSED."""
        cb = CircuitBreaker(fail_max=2, reset_timeout=5)
        cb.record_failure()
        cb.record_failure()
        cb.state = CircuitState.HALF_OPEN

        cb.record_success()
        assert cb.state == CircuitState.CLOSED
        assert cb.fail_count == 0
        assert cb.is_degraded() is False
        assert cb.can_execute() is True

    def test_half_open_trips_to_open_on_failure(self):
        """Неудачный пробный запрос в HALF_OPEN сразу возвращает автомат в OPEN."""
        cb = CircuitBreaker(fail_max=2, reset_timeout=5)
        cb.state = CircuitState.HALF_OPEN
        cb.fail_count = 2

        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        assert cb.is_degraded() is True
