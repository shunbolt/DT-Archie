import discord
from discord.ext import commands
from pickledb import PickleDB

from src.database import database_module 
from src.label import label_module

MENTION_ROLE_NAME = "Archie"

def bot_commands(bot : commands.Bot, database : PickleDB):
    """
    Function to register all bot commands

    Args:
        bot (commands.Bot): Discord bot instance
        database (PickleDB): PickleDB database for storing and querying data 
    """
    # Subfunctions
    # Display embed of quests from member
    def embed_quest_list_from_member(member : discord.member, list_quests : list) -> discord.Embed:
        """Subfunction to build the embed message of the list of quests from a member

        Args:
            member (discord.member): Discord memeber to display quests from
            list_quests (list): List of it's quests from the data
        """
        # Build embed with the quests information
        embed = discord.Embed(title=f"Quêtes de {member.display_name} sur le comptoir de quêtes de la guilde :")
        embed.set_thumbnail(url=member.avatar.url)
        
        for index, quest in enumerate(list_quests):
            quest_index = index + 1
            
            quest_category = label_module.read_category(quest["quest_category"])
            quest_category_name = quest_category["name"]
            quest_category_emoji = quest_category["discord_emoji"]
            quest_label = label_module.read_label(quest["quest_label"])["name"]
            quest_comments = quest["quest_comments"]
            
            # Add emoji based on difficulty tag : implement on a dict directly
            quest_tag = label_module.read_label(quest["quest_label"])["tag"]
            quest_tag_name = label_module.read_tag(quest_tag)["name"]
            quest_tag_emoji = label_module.read_tag(quest_tag)["discord_emoji"]            
            
            embed.add_field(name=f"{quest_category_emoji} Quête {quest_category_name} {quest_tag_name} #{quest_index}",
                            value=f""":label: Nom : {quest_label} {quest_tag_emoji}\n:pencil: Commentaires : {quest_comments}""",
                            inline=False)
        
        return embed
    
    # Sends a message if the member belongs to the role
    async def send_message_with_role(ctx : commands.Context, member : discord.member, required_role : str, msg : str):
        """Sends a message if the member belongs to the given role in the server

        Args:
            member (discord.member): _description_
            required_role (str): _description_
            msg (str): _description_
        """
        # Check if member has the role
        print(member.roles)
        if required_role.lower() in [role.name.lower() for role in member.roles] :
            # Sends message
            await ctx.send(msg)
    
    # Check if the selected label belongs to the dict and send message to relevant members
    async def mention_common_members(ctx : commands.Context, quest_label = None):
        """Get the lists of members having the specified label quests in their list and mentions them in a message

        Args:
            ctx (commands.Context): discord context of the command
            quest_label (_type_, optional): quest label to search for. Defaults to None.
        """
        server_id = str(ctx.guild.id)
        
        if quest_label:
            dict_users_quests = await database_module.get_quests_from_server(database=database,
                                                   server_id=server_id,
                                                   filter_label=quest_label)
            
            # Get the list of members id with common members except yourself
            list_members_id = [user_id for user_id in dict_users_quests.keys() if user_id != str(ctx.author.id)]
            
            for member_id in list_members_id:
                member = bot.get_guild(int(server_id)).get_member(int(member_id))
                print(member)
                await send_message_with_role(ctx=ctx,
                                             member=member,
                                             required_role=MENTION_ROLE_NAME,
                                             msg=f":dart: Le ou la mercenaire {member.mention} est en mesure de t'aider !")
            
            
    # Archie commands 
    # Command to insert a quest to the database
    @bot.command(aliases=["ajout", "add"], help="Ajoute une quête à ton nom")
    async def ajout_quete(ctx : commands.Context, quest_label = None, *, quest_comments = ""):
        """Command to add a quest to the billboard

        Args:
            ctx (discord.Context): discord context of the command
            quest_label (str): first argument corresponding to the label
            If help label is passed, display the list of all possible labels and bosses
            quest_comments (str): second argument as free comments. Defaults to ""
        """
        # Define help labels
        help_labels = ["help", "aide", None]
        
        # Get credentials from the discord context 
        server_id = str(ctx.guild.id)
        user_id = str(ctx.author.id)
        server_name = ctx.guild.name
        user_name = ctx.author.display_name
        
        if (quest_label in help_labels):
            # Read list of all labels
            dict_label = label_module.read_full_label()
            
            # Get list of different tag type
            set_tags_in_dict = list(dict.fromkeys([el.get("tag") for el in dict_label.values()]))
            
            first_embed = True
            for current_tag in set_tags_in_dict:
                # Build list of elements if it belongs to the tag
                list_label_to_display = [f"{label_module.read_tag(value.get('tag'))["discord_emoji"]} **{key}** :arrow_right: {value.get('name')}" 
                                         for key, value in dict_label.items() if value.get('tag') == current_tag]
                
                # Build description and embed from it
                description = "\n\n".join(list_label_to_display)
                
                # display title on the first embed sent
                if first_embed:
                    title = "Labels possible pour la commande `!ajout_quete <label>`"
                    first_embed = False
                else:
                    title = None
                embed = discord.Embed(title=title,
                                    description=description)
                
                await ctx.send(embed=embed)
        else:
            # Read category based on label name
            label_dict = label_module.read_label(quest_label)
            
            if label_dict is not None:
                
                quest_category = label_dict["category"]
                
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
                
                category_translated = label_module.read_category(quest_category)["name"]
                
                await ctx.reply(f"""Le ou la mercenaire {ctx.author.mention} a ajouté la quête suivante sur le comptoir de quêtes de la guilde :\nCatégorie : Quête {category_translated}\nNom : {label_dict["name"]}\nCommentaires : {quest_comments}""")

                # Mention members that have the same label
                await mention_common_members(ctx=ctx, quest_label=quest_label)
            
            else:
                await ctx.send(f"""Aucune quête n'a été trouvée avec le libellé : {quest_label}""")
    
    # Command to get all quests from the current user
    @bot.command(aliases=["lire", "read"], help="Affiches l'ensemble de tes quêtes sous forme d'indices")
    async def lire_quetes(ctx : commands.Context): 
        """Function to read quests from the user on the quest billboard

        Args:
            ctx (discord.Context): discord context of the command
        """
        # Get credentials from the discord context 
        server_id = str(ctx.guild.id)
        user_id = str(ctx.author.id)
        
        list_quests = await database_module.get_quests_from_user(database=database,
                                                   server_id=server_id,
                                                   user_id=user_id)
        
        if list_quests: 
            embed = embed_quest_list_from_member(member=ctx.author, list_quests=list_quests)
                
            await ctx.reply(embed=embed)
        else:
            await ctx.reply("Il n'y a aucune quête à ton nom sur le comptoir : utilise `!ajout_quete` pour en ajouter une !")
    
    # Command to get all quests from the current server
    @bot.command(aliases=["lire_tout", "read_all"], help="Affiches l'ensemble des quêtes de tous les membres du serveur")
    async def lire_toutes_quetes(ctx : commands.Context, quest_label = None): 
        """Function to read all quests from the server

        Args:
            ctx (discord.Context): discord context of the command
            quest_label (str): first optional argument corresponding to the label to filter
        """
        # Get credentials from the discord context 
        server_id = str(ctx.guild.id)
        
        dict_users_quests = await database_module.get_quests_from_server(database=database,
                                                   server_id=server_id,
                                                   filter_label=None)
        
        # If dict is not empty
        if dict_users_quests :
        
            # List all users into a string
            list_user_name = ", ".join([bot.get_guild(int(server_id)).get_member(int(user_id)).display_name for user_id in dict_users_quests.keys()])
                    
            await ctx.reply(f"La liste des membres ayant renseigné une quête sur le comptoir est la suivante : {list_user_name}")
            
            # Build embed for each user with their quests
            for user_id, quest_list in dict_users_quests.items():
                
                embed = embed_quest_list_from_member(bot.get_guild(int(server_id)).get_member(int(user_id)), quest_list)
                
                await ctx.send(embed=embed)  
                
            await mention_common_members(ctx=ctx, quest_label=quest_label)
            
        else:
            if quest_label:
                # Message if there is no quest for the selected label
                await ctx.reply("Il n'y a aucune quête de ce type sur le comptoir : utilise `!ajout_quete` pour en ajouter une!")
            else:
                # Message if there is no quest at all
                await ctx.reply("Il n'y a aucune quête sur le comptoir : utilise `!ajout_quete` pour être le premier à en ajouter!")  
        
    # Command to remove a quest from the user list (passing an index)
    @bot.command(aliases=["del", "supp"], help="Supprimes la quête indexé en argument de ta liste de quête")
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
                await ctx.reply(f"La quête de {ctx.author.display_name} numérotée {arg} a été correctement supprimée")
            else:
                await ctx.send(f"La quête de {ctx.author.display_name} numérotée {arg} n'est pas trouvable")
        else:
            await ctx.send("Numéro d'index inconnu on non reconnu : veuillez réessayer")
        
    # Command to remove a quest from the user list (passing an index)
    bot.remove_command("help")
    
    @bot.command(aliases=["help"])
    async def aide(ctx : commands.Context):
        """Function to display the help text

        Args:
            ctx (commands.Context): discord context of the command
        """
        
        await ctx.send(label_module.read_help())
        