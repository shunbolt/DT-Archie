import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import datetime

# Import modules from src folder
from src.logger import logger_module
from src.events import events_module
from src.commands import commands_module, slash_commands_module
from src.database import database_module

SCRIPT_PATH = os.path.dirname(__file__)
CURRENT_DATE = datetime.date.today().strftime("%Y-%m-%d")


def startup_bot():
    """
    Startup the bot
    """

    # Load env variables
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")
    server_admin_id = int(os.getenv("SERVER_ADMIN_ID"))
    deploy_env = os.getenv("DEPLOY_ENV")
    channel_admin_id_database = int(os.getenv("CHANNEL_ADMIN_ID_DATABASE"))
    channel_admin_id_logs = int(os.getenv("CHANNEL_ADMIN_ID_LOGS"))
    channel_admin_id_cli = int(os.getenv("CHANNEL_ADMIN_ID_CLI"))
    channel_admin_id_restore_database = int(os.getenv("CHANNEL_ADMIN_ID_RESTORE_DATABASE"))
    user_admin_id = int(os.getenv("USER_ADMIN_ID"))

    # Build logger output from the bot
    log_directory = os.path.join(SCRIPT_PATH, "..", "logs")
    if deploy_env == "PROD":
        log_filename = "discord_archie.log"
    else:
        log_filename = f"discord_archie_{CURRENT_DATE}.log"
    handler = logger_module.create_logger(
        path_logfile=log_directory, name_logfile=log_filename, mode="a"
    )

    # Build or instantiate database using pickledb
    database_directory = os.path.join(SCRIPT_PATH, "..", "data")
    database_filename = "discord_archie_data.json"
    database = database_module.create_database(
        path_database=database_directory, name_database=database_filename
    )

    # Setup intents akin to discord dev API page
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    # Setup bot with respective events and commands
    bot = commands.Bot(command_prefix="!", intents=intents)

    # Setup non-admin commands
    slash_commands_module.bot_commands(bot=bot, database=database)

    # Setup admin commands
    commands_module.bot_commands_admin(
        bot=bot,
        database=database,
        database_filepath=os.path.join(database_directory, database_filename),
        log_filepath=os.path.join(log_directory, log_filename),
        server_admin_id=server_admin_id,
        channel_admin_id_database=channel_admin_id_database,
        channel_admin_id_logs=channel_admin_id_logs,
        channel_admin_cli=channel_admin_id_cli,
        channel_admin_id_restore_database=channel_admin_id_restore_database,
        user_admin_id=user_admin_id,
    )

    # Setup events
    events_module.bot_events(
        bot=bot,
        database_filepath=os.path.join(database_directory, database_filename),
        log_filepath=os.path.join(log_directory, log_filename),
        server_admin_id=server_admin_id,
        channel_admin_id_database=channel_admin_id_database,
        channel_admin_id_logs=channel_admin_id_logs,
        user_admin_id=user_admin_id,
    )

    # Run the bot
    
    if deploy_env in ["PROD", "BURN"]:
        log_level = logging.INFO
    else: 
        log_level = logging.DEBUG
    
    bot.run(token, log_handler=handler, log_level=log_level)


if __name__ == "__main__":
    startup_bot()
