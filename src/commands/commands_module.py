from discord.ext import commands
from pickledb import PickleDB

from src.database import database_module

MENTION_ROLE_NAME = "Archie"

def bot_commands_admin(
    bot: commands.Bot,
    database: PickleDB,
    database_filepath: str,
    log_filepath: str,
    server_admin_id: int,
    channel_admin_id_database: int,
    channel_admin_id_logs: int,
    channel_admin_cli: int,
    user_admin_id: int,
):
    """Initialize all events handled by the bot
    launched only through the admin command

    Args:
        bot (commands.Bot): Discord bot
        database_filepath (str) : Path to the database file
        log_filepath (str) : Path to the log file
        server_admin_id (int): id of the admin server
        channel_admin_id_database (int): id of the channel in admin server to send database info
        channel_admin_id_logs (int): id of the channel in admin server to send logs info
        channel_admin_cli (int) : id of the channel in admin server allowed to use commands
        user_admin_id (int): id of the admin server owner
    """

    # Admin launched commands
    def check_admin_command(ctx: commands.Context):
        """
        Checks if the command is passed in the admin server
        in the admin channel
        by the admin user

        Args:
            ctx (commands.Context): Discord context
        """

        if (
            ctx.guild.id == server_admin_id
            and ctx.channel.id == channel_admin_cli
            and ctx.author.id == user_admin_id
        ):
            return True

        return False

    @bot.command()
    @commands.check(check_admin_command)
    async def delete_all(ctx: commands.Context):
        """Purge the whole database

        Args:
            ctx (commands.Context): Discord context
        """

        # Command to delete the whole database
        status_code = await database_module.purge_database(database=database)

        if status_code:
            # Send message confirmation
            await ctx.send("Database successfully deleted")
        else:
            await ctx.send(
                "An error has occurred while purging the database : check logs"
            )

    @bot.command()
    @commands.check(check_admin_command)
    async def delete_server(ctx: commands.Context, server_id: str):
        """Purge all keys sharing the same server

        Args:
            ctx (commands.Context): Discord context
            server_id : id of server to purge
        """

        # Command to delete the server entries of the database
        status_code = await database_module.purge_database_server(
            database=database, server_id=server_id
        )

        if status_code:
            # Send message confirmation
            await ctx.send(
                f"Keys of the server id {server_id} has been successfully deleted"
            )
        else:
            await ctx.send(
                f"There has been some issues with some keys deletion for server id {server_id} : check logs"
            )

    @bot.command()
    @commands.check(check_admin_command)
    async def delete_key(ctx: commands.Context, key_id: str):
        """Purge the key of the database

        Args:
            ctx (commands.Context): Discord context
            key_id : id of server to purge
        """

        # Command to delete the key from the database
        status_code = await database_module.purge_database_key(
            database=database, key=key_id
        )

        if status_code:
            # Send message confirmation
            await ctx.send(f"Key {key_id} has been successfully deleted")
        else:
            await ctx.send(
                f"Key {key_id} couldn't be found or deleted from the database : check logs "
            )
