import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select

from config import config
from database.engine import async_session_maker
from database.models import User
from database.requests import create_order
from keyboards.admin_inline import get_admin_order_kb
from keyboards.order_inline import (
    get_confirm_order_kb,
    get_service_types_kb,
    get_skip_photo_kb,
)
from keyboards.reply import get_main_kb
from states.order import OrderFSM


order_router = Router()
logger = logging.getLogger(__name__)

SERVICE_NAMES = {
    "srv_sewing": "Пошив одежды",
    "srv_repair": "Подгонка и ремонт",
    "srv_consultation": "Консультация стилиста",
}


@order_router.message(F.text == "📝 Оставить заявку")
async def start_order(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(OrderFSM.service_type)
    
    await message.answer(
        text=(
            "📝 <b>Оформление заявки в Ателье «Тори»</b>\n\n"
            "Выберите тип услуги, которая вас интересует:"
        ),
        reply_markup=get_service_types_kb(),
    )


@order_router.callback_query(OrderFSM.service_type, F.data.startswith("srv_"))
async def process_service_type(callback: CallbackQuery, state: FSMContext) -> None:
    service_key = callback.data
    service_name = SERVICE_NAMES.get(service_key, "Неизвестная услуга")
    
    await state.update_data(service_type=service_name, service_key=service_key)
    await state.set_state(OrderFSM.description)
    
    await callback.message.edit_text(
        text=(
            f"✅ Выбрано: <b>{service_name}</b>\n\n"
            "📝 Теперь опишите ваши пожелания:\n\n"
            "• Какая модель одежды?\n"
            "• Какие ткани предпочитаете?\n"
            "• Особые требования к фасону?\n"
            "• Сроки выполнения?\n\n"
            "Напишите всё, что считаете важным."
        )
    )
    await callback.answer()


@order_router.message(OrderFSM.description, F.text)
async def process_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await state.set_state(OrderFSM.photo)
    
    await message.answer(
        text=(
            "✅ Описание принято!\n\n"
            "📸 <b>Прикрепите фото или эскиз</b> (если есть):\n\n"
            "Фотография поможет нашим мастерам лучше понять ваши пожелания.\n"
            "Вы также можете пропустить этот шаг."
        ),
        reply_markup=get_skip_photo_kb(),
    )


@order_router.message(OrderFSM.photo, F.photo)
async def process_photo(message: Message, state: FSMContext) -> None:
    photo_file_id = message.photo[-1].file_id
    await state.update_data(photo_file_id=photo_file_id)
    await state.set_state(OrderFSM.confirmation)
    
    data = await state.get_data()
    preview_text = (
        "📋 <b>Проверьте данные вашей заявки:</b>\n\n"
        f"🧵 <b>Услуга:</b> {data['service_type']}\n"
        f"📝 <b>Описание:</b>\n{data['description']}\n\n"
        "📸 <b>Фото:</b> прикреплено\n\n"
        "✅ Подтвердите отправку заявки в ателье."
    )
    
    await message.answer_photo(
        photo=photo_file_id,
        caption=preview_text,
        reply_markup=get_confirm_order_kb(),
    )


@order_router.callback_query(OrderFSM.photo, F.data == "skip_photo")
async def skip_photo(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(OrderFSM.confirmation)
    data = await state.get_data()
    preview_text = (
        "📋 <b>Проверьте данные вашей заявки:</b>\n\n"
        f"🧵 <b>Услуга:</b> {data['service_type']}\n"
        f"📝 <b>Описание:</b>\n{data['description']}\n\n"
        "✅ Подтвердите отправку заявки в ателье."
    )
    
    await callback.message.edit_text(
        text=preview_text,
        reply_markup=get_confirm_order_kb(),
    )
    await callback.answer()


@order_router.callback_query(OrderFSM.confirmation, F.data == "confirm_order")
async def confirm_order(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    
    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.tg_id == callback.from_user.id)
        )
        user = result.scalar_one()
        
        order = await create_order(
            session=session,
            user_id=user.id,
            service_type=data["service_type"],
            description=data["description"],
            photo_file_id=data.get("photo_file_id"),
        )
        
        admin_text = (
            f"🆕 <b>Новая заявка #{order.id}</b>\n\n"
            f"👤 <b>Клиент:</b> {user.full_name}\n"
            f"📱 <b>Username:</b> @{user.username or 'не указан'}\n"
            f"🆔 <b>Telegram ID:</b> <code>{user.tg_id}</code>\n\n"
            f"🧵 <b>Услуга:</b> {order.service_type}\n"
            f"📝 <b>Описание:</b>\n{order.description}\n\n"
            f"📅 <b>Дата:</b> {order.created_at.strftime('%d.%m.%Y %H:%M')}"
        )
        
        try:
            bot = callback.bot
            admin_kb = get_admin_order_kb(
                order_id=order.id,
                user_tg_id=user.tg_id,
                username=user.username,
            )
            
            if photo_id := data.get("photo_file_id"):
                await bot.send_photo(
                    chat_id=config.ADMIN_ID,
                    photo=photo_id,
                    caption=admin_text,
                    reply_markup=admin_kb,
                )
            else:
                await bot.send_message(
                    chat_id=config.ADMIN_ID,
                    text=admin_text,
                    reply_markup=admin_kb,
                )
        except Exception as e:
            logger.error(f"Failed to notify admin {config.ADMIN_ID}: {e}")
    
    await state.clear()
    
    await callback.message.edit_text(
        text=(
            f"✅ <b>Заявка #{order.id} успешно принята!</b>\n\n"
            "Мастер ателье «Тори» свяжется с вами для уточнения деталей.\n\n"
            "📞 Если возникнут вопросы, звоните:\n"
            "+7 (495) 123-45-67\n\n"
            "Благодарим за обращение! ✨"
        )
    )
    
    await callback.message.answer(
        text="📱 Выберите нужный раздел в меню:",
        reply_markup=get_main_kb(),
    )
    await callback.answer("✅ Заявка отправлена!")


@order_router.callback_query(F.data == "cancel_order")
async def cancel_order(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    
    await callback.message.edit_text(
        text="❌ Оформление заявки отменено.\n\nВы можете начать заново в любой момент."
    )
    
    await callback.message.answer(
        text="📱 Выберите нужный раздел в меню:",
        reply_markup=get_main_kb(),
    )
    await callback.answer("Отменено")

