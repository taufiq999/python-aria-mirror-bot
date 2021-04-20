import os
import shutil
import signal
import time
from sys import executable

import psutil
from pyrogram import idle
from telegram.ext import CommandHandler

from bot import LOGGER, app, bot, botStartTime, dispatcher, updater
from bot.helper.ext_utils import fs_utils
from bot.helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import (
    editMessage,
    sendLogFile,
    sendMessage,
)
from bot.modules import (
    authorize,
    cancel_mirror,
    clone,
    delete,
    list_files,
    mirror,
    mirror_status,
    watch,
)


def stats(update, context):
    currentTime = get_readable_time(time.time() - botStartTime)
    total, used, free = shutil.disk_usage(".")
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)
    recv = get_readable_file_size(psutil.net_io_counters().bytes_recv)
    cpuUsage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    stats = (
        f"<b>Bot Uptime:</b> {currentTime}\n"
        f"<b>Total disk space:</b> {total}\n"
        f"<b>Used:</b> {used}  "
        f"<b>Free:</b> {free}\n\n"
        f"📊Data Usage📊\n<b>Upload:</b> {sent}\n"
        f"<b>Down:</b> {recv}\n\n"
        f"<b>CPU:</b> {cpuUsage}% "
        f"<b>RAM:</b> {memory}% "
        f"<b>Disk:</b> {disk}%"
    )
    sendMessage(stats, context.bot, update)


def start(update, context):
    LOGGER.info(
        "UID: {} - UN: {} - MSG: {}".format(
            update.message.chat.id, update.message.chat.username, update.message.text
        )
    )
    if CustomFilters.authorized_user(update) or CustomFilters.authorized_chat(update):
        if update.message.chat.type == "private":
            sendMessage(
                f"Hey <b>{update.message.chat.first_name}</b>. Welcome to <b>Mirror Bot</b>",
                context.bot,
                update,
            )
        else:
            sendMessage("I'm alive :)", context.bot, update)
    else:
        sendMessage("Oops! not a authorized user.", context.bot, update)


def restart(update, context):
    restart_message = sendMessage("Restarting, Please wait!", context.bot, update)
    # Save restart message ID and chat ID in order to edit it after restarting
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    fs_utils.clean_all()
    os.execl(executable, executable, "-m", "bot")


def ping(update, context):
    start_time = int(round(time.time() * 1000))
    reply = sendMessage("Starting Ping", context.bot, update)
    end_time = int(round(time.time() * 1000))
    editMessage(f"{end_time - start_time} ms", reply)


def log(update, context):
    sendLogFile(context.bot, update)


def bot_help(update, context):

    help_string = f"""
/{BotCommands.MirrorCommand} <b>[url OR magnet_link] OR reply to tg media: Mirror & upload</b>
/{BotCommands.TarMirrorCommand} <b>[url OR magnet_link] OR reply to tg media: Mirror & upload as .tar</b>
/{BotCommands.UnzipMirrorCommand} <b>[url OR magnet_link] OR reply to tg media: Unzip & mirror</b>
/{BotCommands.WatchCommand} <b>[link]: Mirror YT video</b>
/{BotCommands.TarWatchCommand} <b>[link]: Mirror YT video & upload as .tar</b>
/{BotCommands.CloneCommand} <b>[link]: Mirror drive folder</b>
/{BotCommands.CancelMirror} <b>[gid] OR reply to dwnld cmd: Cancel the download</b>
/{BotCommands.StatusCommand} <b>: Shows status of all downloads</b>
/{BotCommands.ListCommand} <b>[query]: search for file/folder</b>
/{BotCommands.StatsCommand} <b>: Show Stats of the machine</b>
/{BotCommands.PingCommand} <b>: Ping!</b>

"""

    help_string_adm = f"""    <b>[Owner only]</b>
/{BotCommands.CancelAllCommand} <b>: Cancel all downloads</b>
/{BotCommands.deleteCommand} <b>[link]: Delete from drive</b>
/{BotCommands.RestartCommand} <b>: Restart bot</b>
/{BotCommands.AuthorizeCommand} <b>: Authorize chat or user</b>
/{BotCommands.UnAuthorizeCommand} <b>: Unauthorize chat or user</b>
/{BotCommands.LogCommand} <b>: Get log file</b>

"""

    if CustomFilters.owner_filter(update):
        sendMessage(help_string + help_string_adm, context.bot, update)
    else:
        sendMessage(help_string, context.bot, update)


def main():
    fs_utils.start_cleanup()
    # Check if the bot is restarting
    if os.path.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        bot.edit_message_text("Restarted successfully!", chat_id, msg_id)
        os.remove(".restartmsg")

    start_handler = CommandHandler(
        BotCommands.StartCommand,
        start,
        filters=CustomFilters.authorized_chat | CustomFilters.authorized_user,
        run_async=True,
    )
    ping_handler = CommandHandler(
        BotCommands.PingCommand,
        ping,
        filters=CustomFilters.authorized_chat | CustomFilters.authorized_user,
        run_async=True,
    )
    restart_handler = CommandHandler(
        BotCommands.RestartCommand,
        restart,
        filters=CustomFilters.owner_filter,
        run_async=True,
    )
    help_handler = CommandHandler(
        BotCommands.HelpCommand,
        bot_help,
        filters=CustomFilters.authorized_chat | CustomFilters.authorized_user,
        run_async=True,
    )
    stats_handler = CommandHandler(
        BotCommands.StatsCommand,
        stats,
        filters=CustomFilters.authorized_chat | CustomFilters.authorized_user,
        run_async=True,
    )
    log_handler = CommandHandler(
        BotCommands.LogCommand, log, filters=CustomFilters.owner_filter, run_async=True
    )
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    updater.start_polling()
    LOGGER.info("Yeah I'm running!")
    signal.signal(signal.SIGINT, fs_utils.exit_clean_up)


app.start()
main()
idle()
