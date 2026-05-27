import asyncio
from types import SimpleNamespace

from app.bot.handlers import (
    handle_admin_approve,
    handle_admin_pending,
    handle_admin_resend_config,
    handle_admin_reset_template,
    handle_admin_template,
    handle_config_request,
    handle_my_traffic,
    handle_request_config_prompt,
    handle_start,
)
from app.bot.ux import MY_TRAFFIC_CALLBACK, REQUEST_CONFIG_PREFIX


def test_handle_start_renders_main_menu_for_admin():
    message = FakeMessage(user_id=9001, first_name="Admin")
    workflow = FakeWorkflow(admin_ids={9001})

    asyncio.run(handle_start(message, workflow=workflow))

    assert "Hello, Admin." in message.answers[0]["text"]
    assert _button_texts(message.answers[0]["reply_markup"])[-1] == ["Admin"]


def test_handle_request_config_prompt_shows_version_choices():
    callback = FakeCallback(
        data=REQUEST_CONFIG_PREFIX,
        user_id=1001,
        username="alice",
        first_name="Alice",
    )

    asyncio.run(handle_request_config_prompt(callback))

    assert "Choose the AmneziaWG config version" in callback.message.answers[0]["text"]
    assert _button_texts(callback.message.answers[0]["reply_markup"]) == [
        ["AmneziaWG 1.5"],
        ["AmneziaWG 2.0"],
    ]
    assert callback.answered is True


def test_handle_config_request_creates_order_for_selected_version():
    callback = FakeCallback(
        data=f"{REQUEST_CONFIG_PREFIX}:amneziawg_v1_5",
        user_id=1001,
        username="alice",
        first_name="Alice",
    )
    workflow = FakeWorkflow(admin_ids={9001})

    asyncio.run(handle_config_request(callback, workflow=workflow))

    assert workflow.requests == [("alice", "amneziawg_v1_5")]
    assert "request #42" in callback.message.answers[0]["text"]
    assert callback.answered is True


def test_handle_my_traffic_renders_user_traffic():
    callback = FakeCallback(
        data=MY_TRAFFIC_CALLBACK,
        user_id=1001,
        username="alice",
        first_name="Alice",
    )
    workflow = FakeWorkflow(admin_ids={9001}, traffic_text_marker="phone")

    asyncio.run(handle_my_traffic(callback, workflow=workflow))

    assert "Your traffic" in callback.message.answers[0]["text"]
    assert "phone" in callback.message.answers[0]["text"]
    assert callback.answered is True


def test_handle_admin_pending_rejects_non_admin():
    callback = FakeCallback(
        data="admin:pending",
        user_id=1001,
        username="alice",
        first_name="Alice",
    )
    workflow = FakeWorkflow(admin_ids={9001})

    asyncio.run(handle_admin_pending(callback, workflow=workflow))

    assert callback.message.answers[0]["text"] == "Admin access required."
    assert callback.answered is True


def test_handle_admin_pending_renders_approve_buttons_for_each_order():
    callback = FakeCallback(
        data="admin:pending",
        user_id=9001,
        username="admin",
        first_name="Admin",
    )
    workflow = FakeWorkflow(admin_ids={9001})

    asyncio.run(handle_admin_pending(callback, workflow=workflow))

    assert "Pending orders" in callback.message.answers[0]["text"]
    assert callback.message.answers[1]["text"] == "Order #11"
    assert _button_texts(callback.message.answers[1]["reply_markup"]) == [
        ["Approve: AmneziaWG 1.5"],
        ["Approve: AmneziaWG 2.0"],
    ]
    assert callback.answered is True


def test_handle_admin_approve_calls_workflow_and_returns_config_preview():
    callback = FakeCallback(
        data="admin:approve:11:amneziawg_v1_5",
        user_id=9001,
        username="admin",
        first_name="Admin",
    )
    workflow = FakeWorkflow(admin_ids={9001})

    asyncio.run(handle_admin_approve(callback, workflow=workflow))

    assert workflow.approvals == [(11, "amneziawg_v1_5")]
    assert "approved" in callback.message.answers[0]["text"]
    assert callback.bot.sent_messages[0]["chat_id"] == 1001
    assert "VPN config is ready" in callback.bot.sent_messages[0]["text"]
    assert callback.bot.sent_documents[0]["chat_id"] == 1001
    assert callback.bot.sent_documents[0]["document"].filename.endswith(".conf")
    assert callback.bot.sent_photos[0]["chat_id"] == 1001
    assert callback.bot.sent_photos[0]["photo"].filename.endswith(".qr.png")
    assert callback.answered is True


def test_handle_admin_approve_rejects_non_admin():
    callback = FakeCallback(
        data="admin:approve:11:amneziawg_v1_5",
        user_id=1001,
        username="alice",
        first_name="Alice",
    )
    workflow = FakeWorkflow(admin_ids={9001})

    asyncio.run(handle_admin_approve(callback, workflow=workflow))

    assert callback.message.answers[0]["text"] == "Admin access required."
    assert workflow.approvals == []
    assert callback.answered is True


def test_handle_admin_template_shows_editable_template_and_reset_button():
    callback = FakeCallback(
        data="admin:templates",
        user_id=9001,
        username="admin",
        first_name="Admin",
    )
    workflow = FakeWorkflow(admin_ids={9001})

    asyncio.run(handle_admin_template(callback, workflow=workflow))

    assert "Config ready template" in callback.message.answers[0]["text"]
    assert "DefaultVPN" in callback.message.answers[0]["text"]
    assert _button_texts(callback.message.answers[0]["reply_markup"]) == [
        ["Reset template"]
    ]
    assert callback.answered is True


def test_handle_admin_reset_template_resets_template():
    callback = FakeCallback(
        data="admin:template:reset",
        user_id=9001,
        username="admin",
        first_name="Admin",
    )
    workflow = FakeWorkflow(admin_ids={9001})

    asyncio.run(handle_admin_reset_template(callback, workflow=workflow))

    assert workflow.template_reset is True
    assert "reset" in callback.message.answers[0]["text"]
    assert callback.answered is True


def test_handle_admin_resend_config_sends_delivery_to_user():
    callback = FakeCallback(
        data="admin:resend:7",
        user_id=9001,
        username="admin",
        first_name="Admin",
    )
    workflow = FakeWorkflow(admin_ids={9001})

    asyncio.run(handle_admin_resend_config(callback, workflow=workflow))

    assert workflow.resends == [7]
    assert callback.bot.sent_messages[0]["chat_id"] == 1001
    assert callback.bot.sent_documents[0]["document"].filename.endswith(".conf")
    assert callback.bot.sent_photos[0]["photo"].filename.endswith(".qr.png")
    assert "resent" in callback.message.answers[0]["text"]
    assert callback.answered is True


class FakeMessage:
    def __init__(self, *, user_id, username=None, first_name=None, last_name=None):
        self.from_user = SimpleNamespace(
            id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        self.answers = []

    async def answer(self, text, reply_markup=None):
        self.answers.append({"text": text, "reply_markup": reply_markup})


class FakeCallback:
    def __init__(self, *, data, user_id, username=None, first_name=None, last_name=None):
        self.data = data
        self.from_user = SimpleNamespace(
            id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        self.message = FakeMessage(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        self.bot = FakeBot()
        self.answered = False

    async def answer(self):
        self.answered = True


class FakeWorkflow:
    def __init__(self, *, admin_ids, traffic_text_marker=None):
        self._admin_ids = admin_ids
        self._traffic_text_marker = traffic_text_marker
        self.requests = []
        self.approvals = []
        self.resends = []
        self.template_reset = False

    def is_admin(self, telegram_id):
        return telegram_id in self._admin_ids

    def request_access(
        self,
        *,
        telegram_id,
        username,
        first_name,
        last_name,
        config_version,
    ):
        self.requests.append((username, config_version))
        return SimpleNamespace(order_id=42, text="Access request #42 was created.")

    def build_user_traffic_views(self, *, telegram_id, now=None):
        return [
            SimpleNamespace(
                device_id=1,
                device_name=self._traffic_text_marker,
                config_version="amneziawg_v2",
                status="active",
                expires_at=None,
                rx="1.0 KiB",
                tx="2.0 KiB",
                total="3.0 KiB",
                collected_at="2026-05-27T12:00:00Z",
                is_available=True,
                is_stale=False,
            )
        ]

    def list_pending_orders(self, *, admin_telegram_id):
        if not self.is_admin(admin_telegram_id):
            return []
        return [
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

    def approve_order(self, *, admin_telegram_id, order_id, config_version):
        if not self.is_admin(admin_telegram_id):
            return None
        self.approvals.append((order_id, config_version))
        return SimpleNamespace(
            device_id=7,
            user_telegram_id=1001,
            admin_text="Access request #11 approved.",
            user_text="Your VPN config is ready.",
            config_text="[Interface]\nPrivateKey = test",
            delivery=SimpleNamespace(
                message_text="Your VPN config is ready.",
                config_filename="amneziya-device-7.conf",
                config_bytes=b"[Interface]\nPrivateKey = test",
                qr_filename="amneziya-device-7.qr.png",
                qr_png_bytes=b"\x89PNG\r\n\x1a\n",
            ),
        )

    def get_config_ready_template(self, *, admin_telegram_id):
        if not self.is_admin(admin_telegram_id):
            return None
        return "DefaultVPN template {device_id}"

    def reset_config_ready_template(self, *, admin_telegram_id):
        if not self.is_admin(admin_telegram_id):
            return False
        self.template_reset = True
        return True

    def build_resend_delivery(self, *, admin_telegram_id, device_id):
        if not self.is_admin(admin_telegram_id):
            return None
        self.resends.append(device_id)
        return SimpleNamespace(
            device_id=device_id,
            user_telegram_id=1001,
            config_text="[Interface]\nPrivateKey = test",
            delivery=SimpleNamespace(
                message_text="Your VPN config is ready.",
                config_filename=f"amneziya-device-{device_id}.conf",
                config_bytes=b"[Interface]\nPrivateKey = test",
                qr_filename=f"amneziya-device-{device_id}.qr.png",
                qr_png_bytes=b"\x89PNG\r\n\x1a\n",
            ),
        )


class FakeBot:
    def __init__(self):
        self.sent_messages = []
        self.sent_documents = []
        self.sent_photos = []

    async def send_message(self, chat_id, text, reply_markup=None):
        self.sent_messages.append(
            {"chat_id": chat_id, "text": text, "reply_markup": reply_markup}
        )

    async def send_document(self, chat_id, document, caption=None):
        self.sent_documents.append(
            {"chat_id": chat_id, "document": document, "caption": caption}
        )

    async def send_photo(self, chat_id, photo, caption=None):
        self.sent_photos.append(
            {"chat_id": chat_id, "photo": photo, "caption": caption}
        )


def _button_texts(markup):
    return [[button.text for button in row] for row in markup.inline_keyboard]
