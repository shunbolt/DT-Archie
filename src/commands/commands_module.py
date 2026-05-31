import discord
import json
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
    channel_admin_id_restore_database: int,
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
        channel_admin_id_restore_database (int) : id of the channel in admin server to read data backup from
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
    async def get_database(ctx: commands.Context):
        """Send the database to the database info channel

        Args:
            ctx (commands.Context): Discord context
        """

        # Look for admin guild
        admin_guild = bot.get_guild(server_admin_id)
        if admin_guild:
            # Look for database channel and send data file
            database_admin_channel = admin_guild.get_channel(channel_admin_id_database)
            if database_admin_channel and isinstance(
                database_admin_channel, discord.TextChannel
            ):
                await database_admin_channel.send(file=discord.File(database_filepath))
        else:
            print("Admin guild not found : please verify specified IDS in env")
            
    @bot.command()
    @commands.check(check_admin_command)
    async def get_logs(ctx: commands.Context):
        """Send the logs to the logs info channel

        Args:
            ctx (commands.Context): Discord context
        """

        # Look for admin guild
        admin_guild = bot.get_guild(server_admin_id)
        if admin_guild:
            # Look for database channel and send data file
            logs_admin_channel = admin_guild.get_channel(channel_admin_id_logs)
            if logs_admin_channel and isinstance(
                logs_admin_channel, discord.TextChannel
            ):
                await logs_admin_channel.send(file=discord.File(log_filepath))
        else:
            print("Admin guild not found : please verify specified IDS in env")

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

    @bot.command()
    @commands.check(check_admin_command)
    async def restore_database(ctx: commands.Context, message_id: str):
        """Use the id passed as message id in the dedicated channel id to resotre database 

        Args:
            ctx (commands.Context): Discord context
            message_id : id of the message to retrieve file from
        """
        
        restore_database_channel = bot.get_channel(channel_admin_id_restore_database)
        
        if restore_database_channel is None:
            await ctx.send("The restore_database id channel hasnt been found : check env value")
            return
        
        try:
            message = await restore_database_channel.fetch_message(int(message_id))
        except discord.NotFound:
            await ctx.send("The message passed in argument couldn't be found")
            return
        except discord.Forbidden:
            await ctx.send("No permission to read message")
            return

        if not message.attachments:
            await ctx.send("No attachments in message")
            return
        
        backup_database_file = await message.attachments[0].read()
        
        try:
            backup_file_content = backup_database_file.decode('utf-8')
            dict_backup = json.loads(backup_file_content)
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            await ctx.send(f"Error parsing file: {e}. Not recognized as JSON file")
            return
        
        await database_module.replace_database(database=database, dict_backup=dict_backup)
        
        await ctx.send("Restored database successfully")