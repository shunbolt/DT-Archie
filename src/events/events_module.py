"""
List of all events handled by the bot
"""

import discord
from discord.ext import commands, tasks

from datetime import time as dtt
from datetime import timezone as tz
from datetime import timedelta as timedelta

FRANCE_TIMEZONE = tz(timedelta(hours=2))


def bot_events(
    bot: commands.Bot,
    database_filepath: str,
    log_filepath: str,
    server_admin_id: int,
    channel_admin_id_database: int,
    channel_admin_id_logs: int,
    user_admin_id: int,
):
    """Initialize all events handled by the bot

    Args:
        bot (commands.Bot): Discord bot
        database_filepath (str) : Path to the database file
        log_filepath (str) : Path to the log file
        server_admin_id (int): id of the admin server
        channel_admin_id_database (int): id of the channel in admin server to send database info
        channel_admin_id_logs (int): id of the channel in admin server to send logs info
        user_admin_id (int): id of the admin server owner
    """

    # Events of the bot to override
    @bot.event
    async def on_ready():
        print(f"We are ready to go in, {bot.user.name}")

        # Sync tree commands
        await bot.tree.sync()

        # Start backup loop coroutine
        send_backup.start()

    @tasks.loop(
        time=dtt(hour=23, minute=50, second=30, tzinfo=FRANCE_TIMEZONE)
    )  # Runs at 23:50:30 UTC2
    async def send_backup():
        # Look for admin guild
        admin_guild = bot.get_guild(server_admin_id)
        if admin_guild:
            # Look for database channel and send data file
            database_admin_channel = admin_guild.get_channel(channel_admin_id_database)
            if database_admin_channel and isinstance(
                database_admin_channel, discord.TextChannel
            ):
                await database_admin_channel.send(file=discord.File(database_filepath))

            logs_admin_channel = admin_guild.get_channel(channel_admin_id_logs)
            if logs_admin_channel and isinstance(
                logs_admin_channel, discord.TextChannel
            ):
                await logs_admin_channel.send(file=discord.File(log_filepath))
        else:
            print("Admin guild not found : please verify specified IDS in env")

    @send_backup.before_loop
    async def before_send_file():
        await bot.wait_until_ready()
