from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy import select

from database.engine import async_session_maker
from database.models import Order, User


menu_router = Router()


@menu_router.message(F.text == "📍 Контакты и адрес")
async def cmd_contacts(message: Message) -> None:
    contacts_text = (
        "📍 <b>Ателье «Тори»</b>\n\n"
        "🏠 <b>Адрес:</b>\n"
        "г. Москва, ул. Мастеров, д. 15, офис 201\n\n"
        "⏰ <b>Часы работы:</b>\n"
        "Пн-Пт: 10:00 - 20:00\n"
        "Сб-Вс: 11:00 - 18:00\n\n"
        "📞 <b>Телефон:</b>\n"
        "+7 (495) 123-45-67\n\n"
        "💬 <b>Мессенджеры:</b>\n"
        "Telegram: @atelier_tori\n"
        "WhatsApp: +7 (495) 123-45-67\n\n"
        "📧 <b>Email:</b>\n"
        "info@atelier-tori.ru\n\n"
        "Будем рады видеть вас! ✨"
    )
    await message.answer(text=contacts_text)


@menu_router.message(F.text == "🧵 Услуги и прайс")
async def cmd_services(message: Message) -> None:
    services_text = (
        "🧵 <b>Услуги Ателье «Тори»</b>\n\n"
        "📋 <b>Индивидуальный пошив:</b>\n"
        "• Платья и юбки — от 5 000 ₽\n"
        "• Брюки и джинсы — от 3 500 ₽\n"
        "• Верхняя одежда (пальто, куртки) — от 12 000 ₽\n"
        "• Костюмы (мужские/женские) — от 15 000 ₽\n"
        "• Свадебные и вечерние наряды — от 25 000 ₽\n\n"
        "✂️ <b>Подгонка по фигуре:</b>\n"
        "• Ушить/расширить — от 800 ₽\n"
        "• Укоротить/удлинить — от 600 ₽\n"
        "• Замена молнии — от 700 ₽\n"
        "• Подгонка плечевой линии — от 1 200 ₽\n\n"
        "🔧 <b>Ремонт и реставрация:</b>\n"
        "• Штопка и заплатки — от 500 ₽\n"
        "• Замена подкладки — от 1 500 ₽\n"
        "• Ремонт карманов — от 600 ₽\n"
        "• Восстановление изделий — от 2 000 ₽\n\n"
        "💬 <b>Консультация стилиста:</b>\n"
        "• Первая консультация — 2 000 ₽\n"
        "• Подбор фасона и тканей — включено\n"
        "• Создание технического эскиза — 1 500 ₽\n\n"
        "💎 <i>Все цены ориентировочные и уточняются индивидуально.</i>\n"
        "📝 Оставьте заявку, и мы подберем оптимальное решение для вас!"
    )
    await message.answer(text=services_text)


@menu_router.message(F.text == "🎨 Придумать эскиз (AI)")
async def cmd_ai_sketch(message: Message) -> None:
    ai_text = (
        "🎨 <b>AI-генератор эскизов</b>\n\n"
        "Уважаемый клиент! Модуль нейросети для автоматической генерации "
        "модных эскизов находится в активной разработке. 🛠\n\n"
        "В ближайшее время вы сможете:\n"
        "• Описать желаемую модель одежды\n"
        "• Получить уникальный fashion-эскиз\n"
        "• Сразу оформить заказ по готовому дизайну\n\n"
        "⏳ Ожидайте обновления! А пока вы можете:\n"
        "📝 Оставить заявку с текстовым описанием\n"
        "💬 Проконсультироваться со стилистом\n\n"
        "Спасибо за понимание! ✨"
    )
    await message.answer(text=ai_text)


@menu_router.message(F.text == "📦 Мои заказы")
async def cmd_my_orders(message: Message) -> None:
    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.tg_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer("❌ Пользователь не найден. Попробуйте отправить /start")
            return
        
        orders_result = await session.execute(
            select(Order).where(Order.user_id == user.id).order_by(Order.created_at.desc())
        )
        orders = orders_result.scalars().all()
        
        if not orders:
            await message.answer(
                "📦 У вас пока нет оформленных заказов в ателье «Тори».\n\n"
                "📝 Нажмите «Оставить заявку», чтобы создать первый заказ!"
            )
            return
        
        status_emoji = {
            "NEW": "🆕",
            "IN_PROGRESS": "⚙️",
            "READY": "✅",
            "CANCELLED": "❌"
        }
        
        status_names = {
            "NEW": "Новый",
            "IN_PROGRESS": "В работе",
            "READY": "Готов к выдаче",
            "CANCELLED": "Отменен"
        }
        
        orders_text = "📦 <b>Ваши заказы в Ателье «Тори»:</b>\n\n"
        for order in orders:
            emoji = status_emoji.get(order.status, "📋")
            status_name = status_names.get(order.status, order.status)
            orders_text += (
                f"{emoji} <b>Заказ #{order.id}</b>\n"
                f"🧵 Услуга: {order.service_type}\n"
                f"📅 Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
                f"📊 Статус: {status_name}\n"
                f"📝 Описание: {order.description[:100]}{'...' if len(order.description) > 100 else ''}\n\n"
            )
        
        orders_text += "💬 По вопросам звоните: +7 (495) 123-45-67"
        await message.answer(text=orders_text)
