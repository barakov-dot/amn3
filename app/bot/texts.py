DEFAULT_LOCALE = "ru"
FALLBACK_LOCALE = "en"


TEXTS = {
    "ru": {
        "button.request_config": "Получить конфиг",
        "button.my_tariff": "Мой тариф",
        "button.my_traffic": "Мой трафик",
        "button.my_devices": "Мои устройства",
        "button.admin": "Админ",
        "button.approve": "Одобрить",
        "button.resend_config": "Отправить конфиг",
        "button.delete_device": "Удалить устройство",
        "button.reset_all_devices": "Сбросить все устройства",
        "button.confirm_delete": "Подтвердить удаление",
        "button.confirm_reset": "Подтвердить сброс",
        "button.pending_orders": "Заявки",
        "button.traffic": "Трафик",
        "button.templates": "Шаблоны",
        "button.users": "Пользователи",
    },
    "en": {
        "button.request_config": "Request config",
        "button.my_tariff": "My tariff",
        "button.my_traffic": "My traffic",
        "button.my_devices": "My devices",
        "button.admin": "Admin",
        "button.approve": "Approve",
        "button.resend_config": "Resend config",
        "button.delete_device": "Delete device",
        "button.reset_all_devices": "Reset all devices",
        "button.confirm_delete": "Confirm delete",
        "button.confirm_reset": "Confirm reset",
        "button.pending_orders": "Pending orders",
        "button.traffic": "Traffic",
        "button.templates": "Templates",
        "button.users": "Users",
    },
}


def text(key: str, *, locale: str = DEFAULT_LOCALE) -> str:
    locale_texts = TEXTS.get(locale, TEXTS[DEFAULT_LOCALE])
    fallback_texts = TEXTS[FALLBACK_LOCALE]
    return locale_texts.get(key, fallback_texts.get(key, key))
