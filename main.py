import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import datetime

# Import modules from src folder 
from src.logger import logger_module
from src.events import events_module
from src.commands import commands_module

SCRIPT_PATH = os.path.dirname(__file__)
CURRENT_DATE = datetime.date.today().strftime("%Y-%m-%d")

def startup_bot():
    """
    Startup the bot
    """
    
    # Load env variables
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')
    
    # Build logger output from the bot
    log_directory = os.path.join(SCRIPT_PATH, "logs")
    log_filename = f"discord_{CURRENT_DATE}.log"
    handler = logger_module.create_logger(path_logfile=log_directory, name_logfile=log_filename, mode='a')
    
    # Setup intents akin to discord dev API page
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    
    # Setup bot with respective events and commands
    bot = commands.Bot(command_prefix='/', intents=intents)
    
    events_module.bot_events(bot)
    commands_module.bot_commands(bot)
    
    bot.run(token, log_handler=handler, log_level=logging.DEBUG)

def main():
    startup_bot()


if __name__ == "__main__":
    main()
