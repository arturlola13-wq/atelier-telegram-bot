from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from database.engine import async_session_maker
from database.requests import set_user
from keyboards.reply import get_main_kb


start_router = Router()


@start_router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    async with async_session_maker() as session:
        await set_user(
            session=session,
            tg_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username,
        )
    
    welcome_text = (
        f"👋 Добро пожаловать, <b>{message.from_user.first_name}</b>!\n\n"
        "🧵 <b>Ателье «Тори»</b> — ваш надежный партнер в создании "
        "идеального гардероба!\n\n"
        "Мы предлагаем:\n"
        "• Пошив одежды любой сложности\n"
        "• Подгонка и ремонт изделий\n"
        "• Консультации по выбору ткани и фасона\n"
        "• AI-генерация модных эскизов\n\n"
        "📱 Выберите нужный раздел в меню ниже:"
    )
    
    await message.answer(text=welcome_text, reply_markup=get_main_kb())
