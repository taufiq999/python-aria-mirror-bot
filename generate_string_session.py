from os import environ

from dotenv import load_dotenv
from pyrogram import Client

# try to load vars from config.env
load_dotenv("config.env")
try:
    API_KEY = environ["TELEGRAM_API"]
    if len(API_KEY) == 0:
        API_KEY = int(input("Enter API KEY: "))
except KeyError:
    API_KEY = int(input("Enter API KEY: "))

try:
    API_HASH = environ["TELEGRAM_HASH"]
    if len(API_HASH) == 0:
        API_HASH = int(input("Enter API KEY: "))
except KeyError:
    API_HASH = int(input("Enter API KEY: "))


with Client(":memory:", api_id=API_KEY, api_hash=API_HASH) as app:
    print(app.export_session_string())
