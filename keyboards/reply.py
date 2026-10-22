from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_main_kb() -> ReplyKeyboardMarkup:
    keyboard = [
        [
            KeyboardButton(text="🧵 Услуги и прайс"),
            KeyboardButton(text="📝 Оставить заявку"),
        ],
        [
            KeyboardButton(text="🎨 Придумать эскиз (AI)"),
            KeyboardButton(text="📦 Мои заказы"),
        ],
        [
            KeyboardButton(text="📍 Контакты и адрес"),
        ],
    ]
    
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
