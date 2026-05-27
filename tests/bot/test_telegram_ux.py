from app.bot.ux import (
    ADMIN_PENDING_CALLBACK,
    ADMIN_TRAFFIC_CALLBACK,
    MY_TRAFFIC_CALLBACK,
    REQUEST_CONFIG_PREFIX,
    VERSION_LABELS,
    build_admin_order_keyboard,
    build_config_version_keyboard,
    build_main_menu,
    render_admin_approval,
    render_admin_pending_orders,
    render_admin_traffic,
    render_user_traffic,
)
from app.services.traffic import DeviceTrafficView


def test_main_menu_shows_user_actions_and_admin_entry_for_admins():
    user_menu = build_main_menu(is_admin=False)
    admin_menu = build_main_menu(is_admin=True)

    assert _button_texts(user_menu) == [["Request config"], ["My traffic"]]
    assert _callback_data(user_menu) == [
        [REQUEST_CONFIG_PREFIX],
        [MY_TRAFFIC_CALLBACK],
    ]
    assert _button_texts(admin_menu)[-1] == ["Admin"]
    assert _callback_data(admin_menu)[-1] == [ADMIN_PENDING_CALLBACK]


def test_config_version_keyboard_offers_amnezia_1_5_and_2_0():
    keyboard = build_config_version_keyboard(prefix=REQUEST_CONFIG_PREFIX)

    assert _button_texts(keyboard) == [
        [VERSION_LABELS["amneziawg_v1_5"]],
        [VERSION_LABELS["amneziawg_v2"]],
    ]
    assert _callback_data(keyboard) == [
        [f"{REQUEST_CONFIG_PREFIX}:amneziawg_v1_5"],
        [f"{REQUEST_CONFIG_PREFIX}:amneziawg_v2"],
    ]


def test_render_user_traffic_lists_devices_and_marks_stale_stats():
    views = [
        DeviceTrafficView(
            device_id=1,
            device_name="phone",
            config_version="amneziawg_v1_5",
            status="active",
            expires_at="2026-06-27T12:00:00Z",
            rx="1.0 KiB",
            tx="2.0 KiB",
            total="3.0 KiB",
            collected_at="2026-05-27T12:00:00Z",
            is_available=True,
            is_stale=False,
        ),
        DeviceTrafficView(
            device_id=2,
            device_name="laptop",
            config_version="amneziawg_v2",
            status="active",
            expires_at=None,
            rx="unavailable",
            tx="unavailable",
            total="unavailable",
            collected_at=None,
            is_available=False,
            is_stale=True,
        ),
    ]

    text = render_user_traffic(views)

    assert "Your traffic" in text
    assert "phone" in text
    assert "AmneziaWG 1.5" in text
    assert "Total: 3.0 KiB" in text
    assert "laptop" in text
    assert "No traffic data yet" in text


def test_admin_pending_orders_render_with_per_order_version_keyboard():
    orders = [
        {
            "id": 11,
            "telegram_id": 1001,
            "username": "alice",
            "first_name": "Alice",
            "last_name": None,
            "status": "manual_review",
            "created_at": "2026-05-27 12:00:00",
        }
    ]

    text = render_admin_pending_orders(orders)
    keyboard = build_admin_order_keyboard(order_id=11)

    assert "Pending orders" in text
    assert "#11" in text
    assert "@alice" in text
    assert _button_texts(keyboard) == [
        [f"Approve: {VERSION_LABELS['amneziawg_v1_5']}"],
        [f"Approve: {VERSION_LABELS['amneziawg_v2']}"],
    ]
    assert _callback_data(keyboard) == [
        ["admin:approve:11:amneziawg_v1_5"],
        ["admin:approve:11:amneziawg_v2"],
    ]


def test_admin_traffic_keyboard_links_pending_orders_and_traffic():
    text, keyboard = render_admin_traffic(
        [
            DeviceTrafficView(
                device_id=7,
                device_name="tablet",
                config_version="amneziawg_v2",
                status="active",
                expires_at=None,
                rx="4.0 KiB",
                tx="8.0 KiB",
                total="12.0 KiB",
                collected_at="2026-05-27T12:00:00Z",
                is_available=True,
                is_stale=False,
            )
        ]
    )

    assert "Admin traffic" in text
    assert "tablet" in text
    assert "12.0 KiB" in text
    assert _callback_data(keyboard) == [[ADMIN_PENDING_CALLBACK], [ADMIN_TRAFFIC_CALLBACK]]


def test_render_admin_approval_mentions_order_device_and_user():
    text = render_admin_approval(
        order_id=11,
        device_id=7,
        user_telegram_id=1001,
        config_version="amneziawg_v2",
    )

    assert "Access request #11 approved" in text
    assert "device #7" in text
    assert "telegram_id=1001" in text
    assert "AmneziaWG 2.0" in text


def _button_texts(markup):
    return [[button.text for button in row] for row in markup.inline_keyboard]


def _callback_data(markup):
    return [[button.callback_data for button in row] for row in markup.inline_keyboard]
