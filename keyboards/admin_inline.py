from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_admin_order_kb(
    order_id: int,
    user_tg_id: int,
    username: str | None = None,
) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(
            text="⚙️ В работу",
            callback_data=f"adm_status:IN_PROGRESS:{order_id}:{user_tg_id}"
        )],
        [InlineKeyboardButton(
            text="👗 Готово к выдаче",
            callback_data=f"adm_status:READY:{order_id}:{user_tg_id}"
        )],
        [InlineKeyboardButton(
            text="❌ Отклонить",
            callback_data=f"adm_status:CANCELLED:{order_id}:{user_tg_id}"
        )],
    ]
    
    if username:
        keyboard.append([
            InlineKeyboardButton(
                text="💬 Написать клиенту",
                url=f"https://t.me/{username}"
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
