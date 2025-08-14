from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types import BufferedInputFile
from config import GeneralConfig as cfg
from bot.process_manager import ProcessManager
from datetime import datetime
from bot.keyboards import get_main_keyboard
from bot.state_manager import StateManager
from bot.scheduler import scheduler, setup_scheduler
from bot.stats_collector import StatsCollector
from help_tools.logger_worker import LoggerWorker

import asyncio
import time
import cv2

project_logger = LoggerWorker().logger
bot = Bot(token=cfg.TG_BOT_TOKEN)
dp = Dispatcher()

process_manager = ProcessManager(project_logger)
state_manager = StateManager(project_logger)

stats_collector = StatsCollector(project_logger)
stats_collector.set_queue(process_manager.kp_queue)


@dp.message(Command("start"))
async def cmd_start(message: Message):
    if message.from_user.id not in cfg.TG_USER_LIST:
        await message.answer(f"❌ Доступ запрещён. {message.from_user.id}")
        project_logger.warning(f"""User {message.from_user.id} tried to use bot!""")
        return
    await message.answer(
        "🐶 Управление отслеживанием собаки.",
        reply_markup=get_main_keyboard(state_manager.is_tracking),
    )


@dp.message(F.text == "Начать отслеживание")
async def start_tracking(message: Message):
    if message.from_user.id not in cfg.TG_USER_LIST:
        return
    if state_manager.is_tracking:
        await message.answer("📹 Уже запущено.")
        return

    if process_manager.start_tracking():
        state_manager.start_tracking()
        stats_collector.start()
        await message.answer(
            "✅ Отслеживание начато.",
            reply_markup=get_main_keyboard(
                state_manager.is_tracking
            ),  # теперь is_tracking = True
        )
        await notify_all_users_about_state(exclude_user_id=message.from_user.id)

    else:
        await message.answer(
            "❌ Ошибка запуска.",
            reply_markup=get_main_keyboard(state_manager.is_tracking),
        )


@dp.message(F.text == "Закончить отслеживание")
async def stop_tracking(message: Message):
    if message.from_user.id not in cfg.TG_USER_LIST:
        return
    if not state_manager.is_tracking:
        await message.answer("❌ Не запущено.")
        return
    if process_manager.stop_tracking():
        state_manager.stop_tracking()
        stats = stats_collector.stop_and_get()
        await message.answer(
            "🛑 Отслеживание остановлено.",
            reply_markup=get_main_keyboard(state_manager.is_tracking),  # False
        )
        await send_stats_to_all_users(stats)

    else:
        await message.answer(
            "❌ Ошибка остановки.",
            reply_markup=get_main_keyboard(state_manager.is_tracking),
        )


@dp.message(F.text == "Сегодня без отслеживания")
async def skip_tracking(message: Message):
    if message.from_user.id not in cfg.TG_USER_LIST:
        return
    state_manager.disable_tracking_today()
    await message.answer(
        "💤 Отслеживание отключено на сегодня.",
        reply_markup=get_main_keyboard(state_manager.is_tracking),
    )


@dp.message(F.text == "Статус")
async def check_status(message: Message):
    if message.from_user.id not in cfg.TG_USER_LIST:
        return

    if state_manager.is_tracking:
        elapsed = (datetime.now() - state_manager.tracking_start_time).total_seconds()
        hours, rem = divmod(int(elapsed), 3600)
        minutes, seconds = divmod(rem, 60)
        duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        tracking_status = f"🟢 Отслеживание активно\n⏱️ Длится: {duration_str}"
    else:
        tracking_status = "🔴 Отслеживание остановлено"

    total_users = len(cfg.TG_USER_LIST)
    status_text = (
        "📋 **Состояние системы**\n\n"
        f"{tracking_status}\n"
        f"👥 Пользователей: {total_users}\n"
        f"📷 Камер: {len(process_manager.cam_hub.processes) if process_manager.cam_hub else 0}\n"
        f"🧠 Нейросеть: {'работает' if process_manager.nn_hub and any(p.is_alive() for p in process_manager.nn_hub.processes.values()) else 'остановлена'}\n"
        f"📅 Без отслеживания сегодня: {'да' if state_manager.tracking_disabled_today else 'нет'}"
    )

    await message.answer(
        status_text,
        parse_mode="Markdown",
        reply_markup=get_main_keyboard(state_manager.is_tracking),
    )


async def auto_stop_tracking():
    if state_manager.is_tracking:
        process_manager.stop_tracking()
        state_manager.stop_tracking()
        stats = stats_collector.stats()
        await send_stats_to_all_users(
            f"⏰ Отслеживание завершено автоматически (9 часов).\n\n📊 {stats}"
        )


async def send_stats_to_all_users(stats: str):
    for uid in cfg.TG_USER_LIST:
        try:
            await bot.send_message(
                uid, stats, reply_markup=get_main_keyboard(state_manager.is_tracking)
            )
        except Exception as e:
            project_logger.error(f"Cannot send message to user {uid}: {e}")


@dp.message(F.text == "Контрольный снимок")
async def take_snapshot(message: Message):
    if message.from_user.id not in cfg.TG_USER_LIST:
        return
    if not state_manager.is_tracking:
        await message.answer("📹 Отслеживание не запущено.")
        return

    process_manager.get_control_frame.value = True
    await message.answer("📸 Делаю снимок...")

    max_wait_time = 5
    start_time = time.time()
    received_any = False

    try:
        while (time.time() - start_time) < max_wait_time:
            try:
                frame = process_manager.control_frames_queue.get(timeout=1.0)
                if not frame:
                    continue

                success, buffer = cv2.imencode(
                    ".jpg", frame.frame, [cv2.IMWRITE_JPEG_QUALITY, 85]
                )
                if not success:
                    print("cv2.imencode failed")
                    continue
                photo = BufferedInputFile(
                    buffer.tobytes(), filename=f"{frame.cam_name}.jpg"
                )

                try:
                    await bot.send_photo(
                        chat_id=message.chat.id,
                        photo=photo,
                        caption=f"📷 Камера: {frame.cam_name}",
                    )
                    received_any = True
                    start_time = time.time()
                except Exception as e:
                    print(f"❌ Ошибка отправки фото: {e}")
            except Exception:
                continue

    except Exception as e:
        await message.answer("❌ Ошибка при получении снимков.")
        process_manager.project_logger.error(f"Error in take_snapshot: {e}")

    finally:
        process_manager.get_control_frame.value = False

    if not received_any:
        await message.answer("❌ Ни один снимок не был получен за 15 секунд.")


async def notify_all_users_about_state(exclude_user_id: int = None):
    """
    Отправляет всем пользователям (кроме exclude_user_id) скрытое сообщение
    с обновлённой клавиатурой, чтобы синхронизировать интерфейс.
    """
    for user_id in cfg.TG_USER_LIST:
        if user_id == exclude_user_id:
            continue  # пропускаем инициатора

        try:
            await bot.send_message(
                chat_id=user_id,
                text="🔄 Состояние системы обновлено.",
                reply_markup=get_main_keyboard(state_manager.is_tracking),
                disable_notification=True,  # без звука
                parse_mode=None,
            )
        except Exception as e:
            error_msg = str(e).lower()
            if "bot was blocked" in error_msg or "user is deactivated" in error_msg:
                # Пользователь заблокировал бота или удалён — можно игнорировать
                project_logger.info(
                    f"User {user_id} blocked bot or deactivated. Skipping."
                )
            else:
                project_logger.error(f"Failed to notify user {user_id}: {e}")


async def main():
    project_logger.info("Запуск Telegram-бота...")
    setup_scheduler(bot, state_manager, process_manager, prj_logger=project_logger)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
