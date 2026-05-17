"""
List of all events handled by the bot 
"""
from discord.ext import commands

def bot_events(bot : commands.Bot):
    """Initialize all events handled by the bot

    Args:
        bot (commands.Bot): Discord bot instance
    """
    
    # Events of the bot to override
    @bot.event
    async def on_ready():
        print(f"We are ready to go in, {bot.user.name}")
        
    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return
        
        if "shit" in message.content.lower():
            await message.delete()
            await message.channel.send(f"{message.author.mention} don't use that word!")
            
        await bot.process_commands(message)