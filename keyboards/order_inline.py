from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_service_types_kb() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="🧵 Пошив одежды", callback_data="srv_sewing")],
        [InlineKeyboardButton(text="✂️ Подгонка и ремонт", callback_data="srv_repair")],
        [InlineKeyboardButton(text="💬 Консультация стилиста", callback_data="srv_consultation")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_skip_photo_kb() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="⏩ Пропустить отправку фото", callback_data="skip_photo")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_confirm_order_kb() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="✅ Подтвердить и отправить", callback_data="confirm_order")],
        [InlineKeyboardButton(text="❌ Отменить заявку", callback_data="cancel_order")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
