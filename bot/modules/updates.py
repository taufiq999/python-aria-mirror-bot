# Implement By https://github.com/jusidama18
# Based on this https://github.com/DevsExpo/FridayUserbot/blob/master/plugins/updater.py

import logging
import subprocess
import sys
from os import environ, execle

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError
from telegram.ext.commandhandler import CommandHandler

from bot import UPSTREAM_BRANCH, UPSTREAM_REPO
from bot.helper.ext_utils.heroku_utils import fetch_heroku_git_url
from bot.helper.ext_utils.sh_utils import runcmd
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import edit_message, send_message

LOGGER = logging.getLogger(__name__)


def update(update, context):
    reply = send_message("Updating... Please wait!", context.bot, update)
    try:
        repo = Repo()
    except GitCommandError:
        return edit_message(
            "**Invalid Git Command. Please Report This Bug On GitHub**", reply
        )
    except InvalidGitRepositoryError:
        repo = Repo.init()
        if "upstream" in repo.remotes:
            origin = repo.remote("upstream")
        else:
            origin = repo.create_remote("upstream", UPSTREAM_REPO)
        origin.fetch()
        repo.create_head(UPSTREAM_BRANCH, origin.refs.master)
        repo.heads.master.set_tracking_branch(origin.refs.master)
        repo.heads.master.checkout(True)
    if repo.active_branch.name != UPSTREAM_BRANCH:
        return edit_message(
            f"`Seems Like You Are Using Custom Branch - {repo.active_branch.name}! Please Switch To {UPSTREAM_BRANCH} To Make This Updater Function!`",
            reply,
        )
    try:
        repo.create_remote("upstream", UPSTREAM_REPO)
    except BaseException:
        pass
    ups_rem = repo.remote("upstream")
    ups_rem.fetch(UPSTREAM_BRANCH)
    HEROKU_URL = fetch_heroku_git_url()
    if not HEROKU_URL:
        try:
            ups_rem.pull(UPSTREAM_BRANCH)
        except GitCommandError:
            repo.git.reset("--hard", "FETCH_HEAD")
        runcmd("pip3 install --no-cache-dir -r requirements.txt")
        edit_message("`Updated Sucessfully! Give Me Some Time To Restart!`", reply)
        subprocess.call("./aria.sh", shell=True)
        args = [sys.executable, "-m", "bot"]
        execle(sys.executable, *args, environ)
    else:
        edit_message("`Heroku Detected! Pushing, Please wait!`", reply)
        ups_rem.fetch(UPSTREAM_BRANCH)
        repo.git.reset("--hard", "FETCH_HEAD")
        if "heroku" in repo.remotes:
            remote = repo.remote("heroku")
            remote.set_url(HEROKU_URL)
        else:
            remote = repo.create_remote("heroku", HEROKU_URL)
        try:
            remote.push(refspec="HEAD:refs/heads/master", force=True)
        except BaseException as error:
            edit_message(f"**Updater Error** \nTraceBack : `{error}`", reply)
            repo.__del__()
        edit_message(
            f"`Updated Sucessfully! \n\nCheck your config with` `/{BotCommands.ConfigMenuCommand}`",
            reply,
        )


restart_handler = CommandHandler(
    BotCommands.RestartCommand,
    update,
    filters=CustomFilters.owner_filter,
    run_async=True,
)
