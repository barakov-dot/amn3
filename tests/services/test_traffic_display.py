from app.services.traffic import build_device_traffic_view, format_bytes


def test_format_bytes_uses_binary_units():
    assert format_bytes(0) == "0 B"
    assert format_bytes(1024) == "1.0 KiB"
    assert format_bytes(1024 * 1024) == "1.0 MiB"


def test_build_device_traffic_view_formats_latest_snapshot():
    device = {
        "id": 7,
        "name": "laptop",
        "config_version": "amneziawg_v2",
        "status": "active",
        "expires_at": "2026-06-03T12:00:00Z",
        "first_connected_at": "2026-05-27T12:00:00Z",
        "last_connected_at": "2026-05-27T12:30:00Z",
    }
    snapshot = {
        "rx_bytes": 1024,
        "tx_bytes": 2048,
        "collected_at": "2026-05-27T12:00:00Z",
    }

    view = build_device_traffic_view(
        device,
        snapshot,
        now="2026-05-27T12:30:00Z",
        stale_after_minutes=60,
    )

    assert view.device_id == 7
    assert view.rx == "1.0 KiB"
    assert view.tx == "2.0 KiB"
    assert view.total == "3.0 KiB"
    assert view.is_stale is False
    assert view.is_available is True
    assert view.is_connected is True
    assert view.first_connected_at == "2026-05-27T12:00:00Z"


def test_build_device_traffic_view_marks_missing_stats_unavailable():
    device = {
        "id": 7,
        "name": "laptop",
        "config_version": "amneziawg_v1_5",
        "status": "active",
        "expires_at": None,
        "first_connected_at": None,
        "last_connected_at": None,
    }

    view = build_device_traffic_view(device, None, now="2026-05-27T12:30:00Z")

    assert view.rx == "unavailable"
    assert view.tx == "unavailable"
    assert view.total == "unavailable"
    assert view.is_available is False
    assert view.is_connected is False


def test_build_device_traffic_view_marks_old_stats_stale():
    device = {
        "id": 7,
        "name": "laptop",
        "config_version": "amneziawg_v2",
        "status": "active",
        "expires_at": None,
    }
    snapshot = {
        "rx_bytes": 1,
        "tx_bytes": 2,
        "collected_at": "2026-05-27T10:00:00Z",
    }

    view = build_device_traffic_view(
        device,
        snapshot,
        now="2026-05-27T12:30:00Z",
        stale_after_minutes=60,
    )

    assert view.is_stale is True
