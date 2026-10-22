import logging
from datetime import datetime

from aiogram import F, Router
from aiogram.types import CallbackQuery

from config import config
from database.engine import async_session_maker
from database.requests import update_order_status


admin_router = Router()
admin_router.callback_query.filter(F.from_user.id == config.ADMIN_ID)
logger = logging.getLogger(__name__)

STATUS_NAMES = {
    "IN_PROGRESS": "⚙️ В работе",
    "READY": "👗 Готово к выдаче",
    "CANCELLED": "❌ Отклонен",
}

CLIENT_NOTIFICATIONS = {
    "IN_PROGRESS": (
        "🧵 <b>Заказ #{order_id} принят в работу!</b>\n\n"
        "Мастер ателье «Тори» приступил к выполнению вашего заказа.\n"
        "Мы уведомим вас, как только заказ будет готов!"
    ),
    "READY": (
        "👗 <b>Ваш заказ #{order_id} готов к выдаче!</b>\n\n"
        "Ждем вас на примерку в ателье «Тори».\n"
        "📍 Адрес: г. Москва, ул. Мастеров, д. 15, офис 201\n"
        "⏰ Часы работы: Пн-Пт 10:00-20:00, Сб-Вс 11:00-18:00\n\n"
        "📞 По всем вопросам: +7 (495) 123-45-67"
    ),
    "CANCELLED": (
        "ℹ️ <b>Заказ #{order_id} отменен.</b>\n\n"
        "Для уточнения деталей вы можете связаться с мастером ателье.\n"
        "📞 Телефон: +7 (495) 123-45-67"
    ),
}


@admin_router.callback_query(F.data.startswith("adm_status:"))
async def process_admin_status_change(callback: CallbackQuery) -> None:
    parts = callback.data.split(":")
    if len(parts) != 4:
        await callback.answer("❌ Ошибка формата данных")
        return
    
    new_status, order_id, user_tg_id = parts[1], int(parts[2]), int(parts[3])
    
    async with async_session_maker() as session:
        if not await update_order_status(session, order_id, new_status):
            await callback.answer("❌ Заказ не найден в базе данных")
            return
    
    status_name = STATUS_NAMES.get(new_status, new_status)
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
    status_update = (
        f"\n\n<b>📊 Текущий статус:</b> {status_name}\n"
        f"<i>⏰ Изменено: {current_time}</i>"
    )
    
    try:
        if callback.message.photo:
            new_caption = (callback.message.caption or "") + status_update
            await callback.message.edit_caption(caption=new_caption, reply_markup=None)
        else:
            new_text = (callback.message.text or "") + status_update
            await callback.message.edit_text(text=new_text, reply_markup=None)
    except Exception as e:
        logger.error(f"Failed to edit admin message: {e}")
    
    if notification_template := CLIENT_NOTIFICATIONS.get(new_status):
        notification_text = notification_template.format(order_id=order_id)
        try:
            await callback.bot.send_message(chat_id=user_tg_id, text=notification_text)
        except Exception as e:
            logger.error(f"Failed to notify user {user_tg_id}: {e}")
    
    await callback.answer("✅ Статус обновлен и клиент уведомлен!")
