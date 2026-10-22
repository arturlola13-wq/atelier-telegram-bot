from aiogram.fsm.state import State, StatesGroup


class OrderFSM(StatesGroup):
    service_type = State()
    description = State()
    photo = State()
    confirmation = State()
