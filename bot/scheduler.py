from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, time as dt_time
from config import GeneralConfig as cfg
from bot.keyboards import get_main_keyboard

scheduler = AsyncIOScheduler(timezone=cfg.TIMEZONE)
bot = None
state_manager = None
process_manager = None

project_logger = None


def setup_scheduler(dp_bot, sm, pm, prj_logger):
    """
    Инициализация планировщика.
    :param dp_bot: экземпляр Bot
    :param sm: экземпляр StateManager
    :param pm: экземпляр ProcessManager
    """
    global bot, state_manager, process_manager, project_logger

    bot = dp_bot
    state_manager = sm
    process_manager = pm
    project_logger = prj_logger

    # Ежедневный запуск цикла напоминаний в 11:00
    scheduler.add_job(
        start_daily_reminder_cycle,
        CronTrigger(hour=11, minute=0, timezone=cfg.TIMEZONE),
        id="start_daily_reminders",
        replace_existing=True,
    )

    # Ежедневный сброс флага "Сегодня без отслеживания" в 00:00
    scheduler.add_job(
        reset_daily_flags,
        CronTrigger(hour=0, minute=0, timezone=cfg.TIMEZONE),
        id="reset_daily_flags",
        replace_existing=True,
    )

    scheduler.start()
    project_logger.info("🗓️ Scheduler запущен.")


async def start_daily_reminder_cycle():
    """
    Запускается каждый день в 11:00.
    Планирует напоминания с 11:05 до 19:05, если отслеживание не запущено.
    """
    current_time = datetime.now().time()
    if current_time >= dt_time(20, 0):
        return

    current_hour = datetime.now().hour
    end_hour = 20
    hours_to_remind = range(max(current_hour, 11), end_hour)

    for hour in hours_to_remind:
        # Планируем напоминание на HH:05
        scheduler.add_job(
            send_reminder_if_needed,
            "cron",
            hour=hour,
            minute=5,
            id=f"reminder_{hour}",
            replace_existing=True,
            timezone=cfg.TIMEZONE,
        )


async def send_reminder_if_needed():
    """
    Отправляет напоминание, если:
    - отслеживание НЕ запущено
    - и НЕ установлен флаг "Сегодня без отслеживания"
    """
    if state_manager.is_tracking or state_manager.tracking_disabled_today:
        project_logger.debug(
            "Напоминание не требуется: отслеживание запущено или отключено на сегодня."
        )
        return

    for user_id in cfg.TG_USER_LIST:
        try:
            await bot.send_message(
                chat_id=user_id,
                text="⏰ Пора начать отслеживание поведения собаки?\n"
                "Хотите начать сейчас?",
                reply_markup=get_main_keyboard(is_tracking=False),
                disable_notification=False,
            )
            project_logger.info(f"📲 Напоминание отправлено пользователю {user_id}")
        except Exception as e:
            error_msg = str(e).lower()
            if "bot was blocked" in error_msg or "user is deactivated" in error_msg:
                project_logger.info(
                    f"Пользователь {user_id} заблокировал бота. Пропускаем."
                )
            else:
                project_logger.error(
                    f"❌ Не удалось отправить напоминание пользователю {user_id}: {e}"
                )


async def reset_daily_flags():
    """
    Выполняется каждый день в 00:00.
    Сбрасывает флаг 'tracking_disabled_today'.
    """
    was_disabled = state_manager.tracking_disabled_today
    state_manager.tracking_disabled_today = False
    if was_disabled:
        project_logger.info("🔁 Флаг 'tracking_disabled_today' сброшен в 00:00.")
