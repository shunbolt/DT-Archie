import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import datetime

SCRIPT_PATH = os.path.dirname(__file__)
CURRENT_DATE = datetime.date.today().strftime("%Y-%m-%d")

HELPER_ROLE_NAME = "Helper"

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
    os.makedirs(name=log_directory, exist_ok=True)
    handler = logging.FileHandler(filename=os.path.join(log_directory, log_filename), mode='w')
    
    # Setup intents akin to discord dev API page
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    
    # Setup bot
    bot = commands.Bot(command_prefix='!', intents=intents)
    
    # Events of the bot
    @bot.event
    async def on_ready():
        print(f"We are ready to go in, {bot.user.name}")
        
    @bot.event
    async def on_member_join(member):
        await member.send(f"Welcome to the server {member.name}")
        
    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return
        
        if "shit" in message.content.lower():
            await message.delete()
            await message.channel.send(f"{message.author.mention} don't use that word!")
            
        await bot.process_commands(message)
    
    # Commands to DM or reply to current channel
    @bot.command()
    async def dm(ctx, *, msg):
        await ctx.author.send(f"You said {msg}")
        
    @bot.command()
    async def reply(ctx):
        await ctx.reply("This is a reply to your message")
        
    # Command to create a pool and add reactions to it
    @bot.command()
    async def poll(ctx, *, question):
        embed = discord.Embed(title="New poll", description=question)
        poll_message = await ctx.send(embed=embed)
        await poll_message.add_reaction("👍")
        await poll_message.add_reaction("👎")
    
    # Commands to send messages and assign / remove existing roles
    @bot.command()
    async def hello(ctx):
        await ctx.send(f"Hello {ctx.author.mention}!")
        
    @bot.command()
    async def assign(ctx):
        role = discord.utils.get(ctx.guild.roles, name=HELPER_ROLE_NAME)
        
        if role:
            await ctx.author.add_roles(role)
            await ctx.send(f"{ctx.author.mention} is now assigned to {HELPER_ROLE_NAME}")
        else:
            await ctx.send("Role does not exist")
        
    @bot.command()
    async def remove(ctx):
        role = discord.utils.get(ctx.guild.roles, name=HELPER_ROLE_NAME)
        
        if role:
            await ctx.author.remove_roles(role)
            await ctx.send(f"{ctx.author.mention} has the {HELPER_ROLE_NAME} role removed")
        else:
            await ctx.send("Role does not exist")
            
    # Commands locked behind roles
    @bot.command()
    @commands.has_role(HELPER_ROLE_NAME)
    async def secret(ctx):
        await ctx.send("Welcome to the helper club !")
    
    @secret.error
    async def secret_error(ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.send("You do not have the permissions to use this command")
    
    bot.run(token, log_handler=handler, log_level=logging.DEBUG)

    
        

def main():
    startup_bot()


if __name__ == "__main__":
    main()
