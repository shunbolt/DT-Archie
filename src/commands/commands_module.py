import discord
from discord.ext import commands
from pickledb import PickleDB

from src.database import database_module 

HELPER_ROLE_NAME = "Helper"

def bot_commands(bot : commands.Bot, database : PickleDB):
    """
    Function to register all bot commands

    Args:
        bot (commands.Bot): Discord bot instance
        database (PickleDB): PickleDB database for storing and querying data 
    """
    
    # Archie command 
    # Command to insert a quest to the database
    @bot.command()
    async def ajout_quete(ctx : commands.Context, arg1 = "", arg2 = "", arg3 = ""):
        """Command to add a quest to the billboard

        Args:
            ctx (discord.Context): discord context of the command
            arg1 (str): first string argument
            arg2 (str): second string argument
            arg3 (str): third string argument
        """
        
        # Get credentials from the discord context 
        server_id = str(ctx.guild.id)
        user_id = str(ctx.author.id)
        server_name = ctx.guild.name
        user_name = ctx.author.name
        
        # HACK : Deduce category and label based on either command launched or argument passed
        # Use typing Literal with elements from a list
        quest_category = arg1
        quest_label = arg2
        quest_comments = arg3
        
        await database_module.insert_quest(
            database=database,
            server_id=server_id,
            user_id=user_id,
            server_name=server_name,
            user_name=user_name,
            quest_category=quest_category,
            quest_label=quest_label,
            quest_comments=quest_comments
        )
        
        await ctx.reply(f"Mercenaire {ctx.author.mention} a ajouté la quête suivante sur le bulletin de la guilde : {quest_category} - {quest_label} - {quest_comments}")
    
    # Command to get all quests from the current user
    @bot.command()
    async def lire_quetes(ctx : commands.Context): 
        """Function to read quests from the user on the billboard

        Args:
            ctx (discord.Context): discord context of the command
        """
        # Get credentials from the discord context 
        server_id = str(ctx.guild.id)
        user_id = str(ctx.author.id)
        
        list_quests = await database_module.get_quests_from_user(database=database,
                                                   server_id=server_id,
                                                   user_id=user_id)
        
        # Build embed with the quests information
        embed = discord.Embed(title=f"Quêtes quotidiennes de {ctx.author.name} :")
        embed.set_thumbnail(url=ctx.author.avatar.url)
        
        for index, quest in enumerate(list_quests):
            quest_index = index + 1
            quest_category = quest["quest_category"]
            quest_label = quest["quest_label"]
            quest_comments = quest["quest_comments"]
            
            embed.add_field(name=f":crossed_swords: Quête {quest_category} #{quest_index}", value=f":label: Libellé : {quest_label}\n:pencil: Commentaires : {quest_comments}", inline=False)
            
        await ctx.reply(embed=embed)
        
    # Command to remove a quest from the user list (passing an index)
    @bot.command()
    async def supp_quete(ctx : commands.Context, arg: int):
        """Function to remove a quest given it's displayed index (offset by 1)

        Args:
            ctx (commands.Context): discord context of the command
            arg : argument expecting an index
        """
        
        # Get credentials from the discord context 
        server_id = str(ctx.guild.id)
        user_id = str(ctx.author.id)
        
        if isinstance(arg, int):
            list_index = arg - 1
            
            status_code = await database_module.remove_quest_from_index(
                database=database,
                server_id=server_id,
                user_id=user_id,
                idx=list_index
            )
            
            if(status_code == 0):
                await ctx.reply(f"La quête de {ctx.author.name} numérotée {arg} a été correctement supprimée")
            else:
                await ctx.send(f"La quête de {ctx.author.name} numérotée {arg} n'est pas trouvable")
        else:
            await ctx.send("Numéro d'index inconnu on non reconnu : veuillez réessayer")
        

        