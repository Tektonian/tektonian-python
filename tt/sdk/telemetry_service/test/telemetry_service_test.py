import json
import threading
from queue import Queue

from pytest import MonkeyPatch

from tt.base.envvar.envvar_service import EnvvarKeyValue, EnvvarService
from tt.sdk.telemetry_service.common import (
    telemetry_service as telemetry_service_module,
)
from tt.sdk.telemetry_service.common.telemetry_service import TelemetryService


class _DummyResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return b"ok"


def _capture_requests(monkeypatch: MonkeyPatch):
    captured_requests: list[dict[str, object]] = []
    sent_event = threading.Event()

    def fake_urlopen(request, timeout):
        captured_requests.append(
            {
                "url": request.full_url,
                "headers": {
                    key.lower(): value for key, value in request.header_items()
                },
                "timeout": timeout,
                "json": json.loads(request.data.decode("utf-8")),
            }
        )
        sent_event.set()
        return _DummyResponse()

    monkeypatch.setattr(telemetry_service_module, "urlopen", fake_urlopen)
    return captured_requests, sent_event


def _build_service(monkeypatch: MonkeyPatch) -> TelemetryService:
    monkeypatch.setenv(EnvvarKeyValue.TT_BASE_URL.value, "https://example.test/api")
    monkeypatch.setenv(EnvvarKeyValue.TT_API_KEY.value, "tt_" + ("a" * 41))
    monkeypatch.delenv(EnvvarKeyValue.TT_TELEMETRY.value, raising=False)

    return TelemetryService(EnvvarService())


def test_public_log_posts_json_to_api_telemetry(monkeypatch: MonkeyPatch):
    captured_requests, sent_event = _capture_requests(monkeypatch)
    service = _build_service(monkeypatch)
    service.BUFFER_FLUSH_TIMEOUT = 0.1

    try:
        service.public_log("environment.created", {"environment_id": "env_0"})

        assert sent_event.wait(timeout=1)

        request = captured_requests[0]
        payload = request["json"]
        event = payload["data"]

        assert request["url"] == "https://example.test/api/telemetry/simulac"
        assert request["headers"]["content-type"] == "application/json"
        assert payload["sdk"] == "simulac-python"
        assert event["event_name"] == "environment.created"
        assert event["level"] == "usage"
        assert event["data"] == {"environment_id": "env_0"}
    finally:
        service._close()


def test_close_flushes_buffered_events(monkeypatch: MonkeyPatch):
    captured_requests, _ = _capture_requests(monkeypatch)
    service = _build_service(monkeypatch)
    service.BUFFER_FLUSH_TIMEOUT = 60

    service.public_error("runner.crashed", {"reason": "timeout"})
    service._close()

    assert len(captured_requests) == 1

    request = captured_requests[0]
    payload = request["json"]
    event = payload["data"]

    assert request["url"] == "https://example.test/api/telemetry/simulac"
    assert event["event_name"] == "runner.crashed"
    assert event["level"] == "error"
    assert event["data"] == {"reason": "timeout"}


def test_flush_when_process_close(monkeypatch: MonkeyPatch):
    registered: dict[str, object] = {}
    captured_requests, _ = _capture_requests(monkeypatch)

    def fake_register(callback):
        registered["callback"] = callback
        return callback

    monkeypatch.setattr(telemetry_service_module.atexit, "register", fake_register)

    service = _build_service(monkeypatch)
    service.BUFFER_FLUSH_TIMEOUT = 60

    service.public_log("process.exiting", {"reason": "normal-exit"})

    close_callback = registered["callback"]
    close_callback()

    assert len(captured_requests) == 1

    request = captured_requests[0]
    payload = request["json"]
    event = payload["data"]

    assert request["url"] == "https://example.test/api/telemetry/simulac"
    assert event["event_name"] == "process.exiting"
    assert event["data"] == {"reason": "normal-exit"}


def test_timeout_handling(monkeypatch: MonkeyPatch):
    attempts: list[tuple[str, float]] = []

    def fake_urlopen(request, timeout):
        attempts.append((request.full_url, timeout))
        raise TimeoutError("network timeout")

    monkeypatch.setattr(telemetry_service_module, "urlopen", fake_urlopen)

    service = _build_service(monkeypatch)
    service.BUFFER_FLUSH_TIMEOUT = 60

    service.public_error("network.timeout", {"retry": True})
    service._close()

    assert len(attempts) == 2
    assert attempts[0][0] == "https://example.test/api/telemetry/simulac"
    assert attempts[1][0] == "https://example.test/api/telemetry/simulac"
    assert attempts[0][1] == service.REQUEST_TIMEOUT
    assert attempts[1][1] == service.REQUEST_TIMEOUT
    assert service.telemetry_thread is not None
    assert not service.telemetry_thread.is_alive()


def test_maximum_queue_size(monkeypatch: MonkeyPatch):
    captured_requests, _ = _capture_requests(monkeypatch)
    service = _build_service(monkeypatch)
    service.BUFFER_SIZE_LIMIT = 2
    service._queue = Queue(maxsize=2)
    monkeypatch.setattr(service, "_ensure_worker", lambda: True)

    service.public_log("event.1", {"order": 1})
    service.public_log("event.2", {"order": 2})
    service.public_log("event.3", {"order": 3})

    batch: list[dict[str, object]] = []
    while not service._queue.empty():
        batch.append(service._queue.get_nowait())

    service._send_batch(batch)

    assert len(captured_requests) == 3

    events = [request["json"]["data"] for request in captured_requests]

    assert [event["event_name"] for event in events] == [
        "telemetry.events_dropped",
        "event.2",
        "event.3",
    ]
    assert events[0]["data"] == {"count": 1}
    assert events[1]["data"] == {"order": 2}
    assert events[2]["data"] == {"order": 3}
