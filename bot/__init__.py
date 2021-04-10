import faulthandler
import logging
import os
import socket
import threading
import time

import aria2p
import telegram.ext as tg
from dotenv import load_dotenv
from pyrogram import Client


def getConfig(name: str):
    return os.environ[name]


faulthandler.enable()
socket.setdefaulttimeout(600)

try:
    with open("log.txt", "r+") as f:
        f.truncate(0)
except FileNotFoundError:
    pass

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)
LOGGER = logging.getLogger(__name__)

load_dotenv("config.env")

try:
    if bool(getConfig("_____REMOVE_THIS_LINE_____")):
        LOGGER.error("The README.md file is there to be read! Exiting now!")
        exit()
except KeyError:
    pass

aria2 = aria2p.API(
    aria2p.Client(
        host="http://localhost",
        port=6800,
        secret="",
    )
)

DOWNLOAD_DIR = None
BOT_TOKEN = None

botStartTime = time.time()
Interval = []

download_dict_lock = threading.Lock()
status_reply_dict_lock = threading.Lock()
# Key: update.effective_chat.id
# Value: telegram.Message
status_reply_dict = {}
# Key: update.message.message_id
# Value: An object of Status
download_dict = {}

try:
    LOGGER.info("Loading environment variables...")
    BOT_TOKEN = getConfig("BOT_TOKEN")
    parent_id = getConfig("GDRIVE_FOLDER_ID")
    DOWNLOAD_DIR = getConfig("DOWNLOAD_DIR")
    if not DOWNLOAD_DIR.endswith("/"):
        DOWNLOAD_DIR = DOWNLOAD_DIR + '/'
    DOWNLOAD_STATUS_UPDATE_INTERVAL = int(getConfig("DOWNLOAD_STATUS_UPDATE_INTERVAL"))
    OWNER_ID = int(getConfig("OWNER_ID"))
    AUTO_DELETE_MESSAGE_DURATION = int(getConfig("AUTO_DELETE_MESSAGE_DURATION"))
    TELEGRAM_API = getConfig("TELEGRAM_API")
    TELEGRAM_HASH = getConfig("TELEGRAM_HASH")
except KeyError as e:
    LOGGER.error("One or more env variables missing! Exiting now")
    exit(1)

LOGGER.info("Generating USER_SESSION_STRING")
app = Client(
    ":memory:", api_id=int(TELEGRAM_API), api_hash=TELEGRAM_HASH, bot_token=BOT_TOKEN
)

# Stores list of users and chats the bot is authorized to use in
AUTHORIZED_CHATS = set()
try:
    with open("authorized_chats.txt", "r+") as f:
        lines = f.readlines()
        for line in lines:
            AUTHORIZED_CHATS.add(int(line.split()[0]))
except FileNotFoundError:
    pass
try:
    for chats in getConfig("AUTHORIZED_CHATS").split(" "):
        AUTHORIZED_CHATS.add(int(chats))
except:
    pass

try:
    INDEX_URL = getConfig("INDEX_URL")
    if len(INDEX_URL) == 0:
        INDEX_URL = None
except KeyError:
    INDEX_URL = None
try:
    IS_TEAM_DRIVE = getConfig("IS_TEAM_DRIVE").lower() == "true"
except KeyError:
    IS_TEAM_DRIVE = False

try:
    USE_SERVICE_ACCOUNTS = getConfig("USE_SERVICE_ACCOUNTS").lower() == "true"
except KeyError:
    USE_SERVICE_ACCOUNTS = False

updater = tg.Updater(token=BOT_TOKEN)
bot = updater.bot
dispatcher = updater.dispatcher
