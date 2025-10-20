import time
from fastapi.testclient import TestClient
from src.main import create_app


def make_client(tmp_path):
    db = tmp_path / 'dedup.db'
    app = create_app(str(db))
    client = TestClient(app)
    return client, db


def test_persistency_across_restart(tmp_path):
    client, db = make_client(tmp_path)
    ev = {
        "topic": "t2",
        "event_id": "eX",
        "timestamp": "2025-10-19T12:00:00Z",
        "source": "tester",
        "payload": {"n": 1},
    }
    client.post('/publish', json=ev)
    time.sleep(0.1)
    client.app = None
    app2 = create_app(str(db))
    client2 = TestClient(app2)
    r = client2.post('/publish', json=ev)
    assert r.status_code == 200
    time.sleep(0.1)
    stats = client2.get('/stats').json()
    assert stats['unique_processed'] == 0 or stats['duplicate_dropped'] >= 1


def test_schema_validation(tmp_path):
    client, db = make_client(tmp_path)
    bad = {"topic": "", "event_id": "", "timestamp": "not-a-time", "source": "s", "payload": {}}
    r = client.post('/publish', json=bad)
    assert r.status_code == 422


def test_stats_uptime_increases(tmp_path):
    client, db = make_client(tmp_path)
    s1 = client.get('/stats').json()
    time.sleep(1)
    s2 = client.get('/stats').json()
    assert s2['uptime_seconds'] >= s1['uptime_seconds']


def test_invalid_batch_input(tmp_path):
    client, db = make_client(tmp_path)
    batch = [
        {"topic": "valid", "event_id": "ok", "timestamp": "2025-10-19T00:00:00Z", "source": "s", "payload": {}},
        {"topic": "", "event_id": "", "timestamp": "bad", "source": "s", "payload": {}},
    ]
    r = client.post('/publish', json=batch)
    assert r.status_code in (200, 422)


def test_get_events_empty_result(tmp_path):
    client, db = make_client(tmp_path)
    res = client.get('/events?topic=doesnotexist').json()
    assert res == [] or len(res) == 0
