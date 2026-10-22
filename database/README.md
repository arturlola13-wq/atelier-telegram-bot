# Слой данных (Database Layer)

Реализация Этапа 1 из ROADMAP.md — слой данных на базе SQLAlchemy 2.0 и SQLite.

## Структура

```
database/
├── __init__.py          # Инициализация модуля
├── models.py            # Модели User и Order
├── engine.py            # Асинхронный движок и фабрика сессий
└── requests.py          # CRUD-функции для работы с БД
```

## Модели данных

### User (Пользователь)
- `id` — Primary Key (autoincrement)
- `tg_id` — Telegram ID (BigInteger, unique, indexed)
- `full_name` — Полное имя пользователя
- `username` — Никнейм @username (опционально)
- `phone` — Номер телефона (опционально)
- `created_at` — Дата регистрации (автоматически)

### Order (Заказ)
- `id` — Primary Key (номер заказа)
- `user_id` — Foreign Key на users.id (CASCADE)
- `service_type` — Категория услуги (Пошив/Подгонка/Ремонт)
- `description` — Текстовое описание заказа
- `photo_file_id` — ID фото в Telegram (опционально)
- `sketch_url` — URL сгенерированного эскиза (опционально)
- `status` — Статус заказа (NEW/IN_PROGRESS/READY/CANCELLED), по умолчанию NEW
- `created_at` — Дата создания (автоматически)

## Использование

### Инициализация базы данных

```python
from database.engine import init_db

# При старте приложения
await init_db()
```

### Работа с пользователями

```python
from database.engine import async_session_maker
from database.requests import set_user

# Создание или обновление пользователя (upsert)
async with async_session_maker() as session:
    user = await set_user(
        session=session,
        tg_id=123456789,
        full_name="Иван Иванов",
        username="ivanov"  # опционально
    )
    print(user)
```

## Технические детали

- **База данных**: SQLite через aiosqlite
- **ORM**: SQLAlchemy 2.0 с современным синтаксисом (Mapped, mapped_column)
- **Асинхронность**: Полностью async/await
- **Типизация**: Строгие type hints для всех функций и атрибутов
- **Upsert**: Безопасное создание/обновление через on_conflict_do_update

## Зависимости

```
SQLAlchemy==2.0.36
aiosqlite==0.20.0
```

## Тестирование

Запустите тестовый скрипт из корня проекта:

```bash
python test_database.py
```

Это создаст базу данных `atelier.sqlite3` и выполнит базовые операции с пользователями.
