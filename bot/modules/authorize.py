from bot import AUTHORIZED_CHATS, dispatcher
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import sendMessage
from telegram import Update
from telegram.ext import CommandHandler, Filters, run_async


@run_async
def authorize(update, context):
    reply_message = update.message.reply_to_message
    msg = ""
    with open("authorized_chats.txt", "a") as file:
        if reply_message is None:
            # Trying to authorize a chat
            chat_id = update.effective_chat.id
            if chat_id not in AUTHORIZED_CHATS:
                file.write(f"{chat_id}\n")
                AUTHORIZED_CHATS.add(chat_id)
                msg = f"Chat authorized: <i>{chat_id}</i>"
            else:
                msg = f"Already authorized chat: <i>{chat_id}</i>"
        else:
            # Trying to authorize someone in specific
            user_id = reply_message.from_user.id
            if user_id not in AUTHORIZED_CHATS:
                file.write(f"{user_id}\n")
                AUTHORIZED_CHATS.add(user_id)
                msg = f"Person Authorized to use the bot!: <i>{user_id}</i>"
            else:
                msg = f"Person already authorized: <i>{user_id}</i>"
        sendMessage(msg, context.bot, update)


@run_async
def unauthorize(update, context):
    reply_message = update.message.reply_to_message
    if reply_message is None:
        # Trying to unauthorize a chat
        chat_id = update.effective_chat.id
        if chat_id in AUTHORIZED_CHATS:
            AUTHORIZED_CHATS.remove(chat_id)
            msg = f"Chat unauthorized: <i>{chat_id}</i>"
        else:
            msg = f"Already unauthorized chat: <i>{chat_id}</i>"
    else:
        # Trying to authorize someone in specific
        user_id = reply_message.from_user.id
        if user_id in AUTHORIZED_CHATS:
            AUTHORIZED_CHATS.remove(user_id)
            msg = f"Person unauthorized to use the bot!: <i>{user_id}</i>"
        else:
            msg = f"Person already unauthorized!: <i>{user_id}</i>"
    with open("authorized_chats.txt", "a") as file:
        file.truncate(0)
        for i in AUTHORIZED_CHATS:
            file.write(f"{i}\n")
    sendMessage(msg, context.bot, update)


authorize_handler = CommandHandler(
    command=BotCommands.AuthorizeCommand,
    callback=authorize,
    filters=CustomFilters.owner_filter & Filters.group,
)
unauthorize_handler = CommandHandler(
    command=BotCommands.UnAuthorizeCommand,
    callback=unauthorize,
    filters=CustomFilters.owner_filter & Filters.group,
)
dispatcher.add_handler(authorize_handler)
dispatcher.add_handler(unauthorize_handler)
