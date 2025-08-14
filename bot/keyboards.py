from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard(is_tracking: bool):
    """
    Генерирует клавиатуру в зависимости от состояния отслеживания.
    """
    buttons = []

    if is_tracking:
        buttons.append([KeyboardButton(text="Закончить отслеживание")])
        buttons.append([KeyboardButton(text="Контрольный снимок")])
    else:
        buttons.append([KeyboardButton(text="Начать отслеживание")])
        buttons.append([KeyboardButton(text="Сегодня без отслеживания")])

    buttons.append([KeyboardButton(text="Статус")])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
    )
