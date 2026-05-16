import discord
from discord.ext import commands

HELPER_ROLE_NAME = "Helper"

def bot_commands(bot : commands.Bot):
    """

    Args:
        bot (commands.Bot): _description_
    """
    
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