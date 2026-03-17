"""Tests for app.utils.retry"""

import pytest
from unittest.mock import MagicMock, patch

from app.utils.retry import retry_with_backoff, RetryableAPIClient


# ── retry_with_backoff decorator ───────────────────────────────────

def test_retry_succeeds_first_try():
    call_count = 0

    @retry_with_backoff(max_retries=3, initial_delay=0, jitter=False)
    def succeed():
        nonlocal call_count
        call_count += 1
        return "ok"

    result = succeed()
    assert result == "ok"
    assert call_count == 1


def test_retry_succeeds_after_failure():
    call_count = 0

    @retry_with_backoff(max_retries=3, initial_delay=0, jitter=False)
    def fail_once():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ValueError("temporary error")
        return "recovered"

    result = fail_once()
    assert result == "recovered"
    assert call_count == 2


def test_retry_exhausted():
    call_count = 0

    @retry_with_backoff(max_retries=2, initial_delay=0, jitter=False)
    def always_fail():
        nonlocal call_count
        call_count += 1
        raise RuntimeError("permanent error")

    with pytest.raises(RuntimeError, match="permanent error"):
        always_fail()

    # initial attempt + 2 retries = 3 total
    assert call_count == 3


def test_on_retry_callback():
    callback = MagicMock()

    @retry_with_backoff(max_retries=2, initial_delay=0, jitter=False, on_retry=callback)
    def fail_then_succeed():
        if callback.call_count < 1:
            raise ValueError("oops")
        return "done"

    result = fail_then_succeed()
    assert result == "done"
    # on_retry is called with (exception, attempt_number)
    callback.assert_called_once()
    args = callback.call_args[0]
    assert isinstance(args[0], ValueError)
    assert args[1] == 1  # first retry attempt


# ── RetryableAPIClient ────────────────────────────────────────────

def test_retryable_api_client_success():
    client = RetryableAPIClient(max_retries=2, initial_delay=0)

    # Patch time.sleep to avoid any accidental real sleeps
    with patch("app.utils.retry.time.sleep"):
        result = client.call_with_retry(lambda x: x * 2, 5)

    assert result == 10


def test_retryable_api_client_failure():
    client = RetryableAPIClient(max_retries=1, initial_delay=0)

    def boom(x):
        raise RuntimeError("fail")

    with patch("app.utils.retry.time.sleep"):
        with pytest.raises(RuntimeError, match="fail"):
            client.call_with_retry(boom, 1)


def test_batch_with_retry():
    client = RetryableAPIClient(max_retries=1, initial_delay=0)

    def process(item):
        if item == "bad":
            raise ValueError("bad item")
        return item.upper()

    with patch("app.utils.retry.time.sleep"):
        successes, failures = client.call_batch_with_retry(
            items=["hello", "bad", "world"],
            process_func=process,
        )

    assert successes == ["HELLO", "WORLD"]
    assert len(failures) == 1
    assert failures[0]["item"] == "bad"
    assert failures[0]["index"] == 1
