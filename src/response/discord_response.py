"""
Functions that generate responses for the bot
"""

from zoneinfo import ZoneInfo

import discord
from discord.ext import commands

from src.label import label_module
from src.database import database_module
from pickledb import PickleDB
        
async def send_message_from_interaction(
    interaction : discord.interaction,
    is_followup : bool,
    msg : str,
    embed = None,
):
    """Send message from interaction given if it's a followup or a direct message to send

    Args:
        msg (str): message to send or followup
        is_followup (bool): determine if the message is a followup or not
        embed : embed to send
    """
    if is_followup:
        await interaction.followup.send(
                content=msg,
                embed=embed,
        )
    else:
        await interaction.response.send_message(
                content=msg,
                embed=embed,
        )
            

def embed_quest_list_from_member(
        member: discord.member, list_quests: list, hide_index=False
    ) -> discord.Embed:
        """Build the embed message of the list of quests from a member

        Args:
            member (discord.member): Discord member to display quests from
            list_quests (list): List of it's quests from the data
            hide_index (bool): boolean to hide index value for embed. Defaults to false
        """
        # Build embed with the quests information
        embed = discord.Embed(
            title=f"Quêtes de {member.display_name} sur le comptoir de la guilde :"
        )
        embed.set_thumbnail(url=member.avatar.url)

        for index, quest in enumerate(list_quests):
            # Get index for the quest
            if hide_index:
                quest_index = ""
            else:
                quest_index = f"`#{index + 1}`"
                
            # Get helper value
            quest_helper_flag = quest.get("helper_flag")

            # Adjust quest_prefix based on helper flag value
            if quest_helper_flag:
                quest_prefix = ":star2: :star2: :star2: Passeur de quête"
            else:
                quest_prefix = "Quête"

            # Get quest components to display
            quest_category = label_module.read_category(quest["quest_category"])
            quest_category_name = quest_category["name"]
            quest_category_emoji = quest_category["discord_emoji"]
            quest_label = label_module.read_label(quest["quest_label"])["name"]
            quest_comments = quest["quest_comments"]
            quest_datetime = quest.get("quest_datetime")

            # Add emoji based on difficulty tag : implement on a dict directly
            quest_tag = label_module.read_label(quest["quest_label"])["tag"]
            quest_tag_name = label_module.read_tag(quest_tag)["name"]
            quest_tag_emoji = label_module.read_tag(quest_tag)["discord_emoji"]

            embed_name = f"{quest_category_emoji} {quest_prefix} {quest_category_name} {quest_tag_name} {quest_tag_emoji} {quest_index}"

            embed.add_field(
                name=embed_name,
                value=f""":label: Nom : {quest_label}\n:pencil: Commentaires : {quest_comments}\n:date: Publiée le : {quest_datetime}""",
                inline=False,
            )

        return embed

async def mention_common_members(
    bot : commands.Bot, interaction: discord.Interaction, database: PickleDB, quest_label=None, from_helper=False,
):
    """Get the lists of members having the specified label quests in their list and mentions them in a message

    Args:
        ctx (commands.Context): discord context of the command
        quest_label (str, optional): quest label to search for. Defaults to None.
        from_helper (bool, optional): tells if the trigger comes from an helper or not. Defaults to false 
    """
    server_id = str(interaction.guild.id)

    if quest_label:
        # Get all quests from the given label
        dict_users_quests = await database_module.get_quests_from_server(
            database=database, server_id=server_id, filter_label=quest_label
        )

        # Get the list of members who has the given quest label in their list except yourself
        list_members_id = [
            user_id
            for user_id in dict_users_quests.keys()
            if user_id != str(interaction.user.id)
        ]
        
        # Get the list of helpers who has the given quest label in their list except yourself
        helper_members_id = [
            user_id
            for user_id in dict_users_quests.keys()
            if user_id != str(interaction.user.id) and any([el.get("helper_flag") for el in dict_users_quests[user_id]])
        ]

        # Loop to mention the members 
        for member_id in list_members_id:
            member = bot.get_guild(int(server_id)).get_member(int(member_id))
            
            if from_helper:
                # Message to send when the user is providing assistance : only search for members who are not helpers
                if member_id not in helper_members_id:
                    message = f":sos: Mercenaire {member.mention} cherches un passeur pour l'aider dans cette même quête"
            else:
                # Messages to send if the user asks for help through a quest
                if member_id in helper_members_id:
                    message = f":sparkles: Mercenaire {member.mention} est un passeur qui peut t'aider à accomplir ta quête !"
                else:
                    message = f":dart: Mercenaire {member.mention} partage la même quête que toi et peut t'aider !"
            
            await interaction.followup.send(content=message)

async def add_quest_to_database(
    bot : commands.Bot, 
    interaction: discord.Interaction, 
    database: PickleDB,
    quest_label: str,
    quest_comments : str = "",
    is_helper: bool = False,
    is_followup: bool = False):
    
    # Get info from interaction object 
    server_id = str(interaction.guild.id)
    user_id = str(interaction.user.id)
    server_name = interaction.guild.name
    user_name = interaction.user.display_name
    
    # Correct quest_comments if None is passed
    if quest_comments is None:
        quest_comments = ""
    
    # Read category based on label name
    label_dict = label_module.read_label(quest_label)
    
    # Get the current datetime of the message to insert in the quest metadata
    quest_datetime = interaction.created_at.astimezone(ZoneInfo("Europe/Paris")).strftime('%Y-%m-%d %H:%M:%S')

    # If matching quest is found
    if label_dict is not None:
        # Set the category from the list of quests
        quest_category = label_dict["category"]

        # Build the dictionary to add to the database
        quest_dict = {
            "server_name": server_name,
            "user_name": user_name,
            "quest_category": quest_category,
            "quest_label": quest_label,
            "quest_comments": quest_comments,
            "helper_flag": is_helper,
            "quest_datetime" : quest_datetime
        }

        await database_module.insert_quest(
            database=database,
            server_id=server_id,
            user_id=user_id,
            server_name=server_name,
            user_name=user_name,
            quest_category=quest_category,
            quest_label=quest_label,
            quest_comments=quest_comments,
            helper_flag=is_helper,
            quest_datetime=quest_datetime,
        )

        # Build the embed of the newly added quest to display
        quest_embed = embed_quest_list_from_member(
            interaction.user, [quest_dict], hide_index=True
        )
        
        # Change message based on helper flag value
        msg = ""
        if is_helper:
            msg = f":raised_hand: Mercenaire {interaction.user.mention} s'est porté volontaire comme passeur à la quête suivante :"
        else:
            msg=f":bell: Mercenaire {interaction.user.mention} a ajouté la quête suivante sur le comptoir de quêtes de la guilde :"
    
        await send_message_from_interaction(
            interaction=interaction,
            is_followup=is_followup,
            msg=msg,
            embed=quest_embed
        )

        # Mention members that share the same label
        await mention_common_members(
            bot=bot, interaction=interaction, database=database, quest_label=quest_label, from_helper=is_helper
        )

    else:
        # Error message when typed quest haven't been found
        await interaction.response.send_message(
            content=f"""Aucune quête n'a été trouvée avec le libellé : {quest_label}"""
        )
            
async def display_labels(interaction : discord.Interaction) -> list:
    """Display the list of all possible labels into a list of Embeds

    Returns:
        embed_list : List of embeds
    """
    
    # Read list of all labels
    dict_label = label_module.read_full_label()

    # Get list of different tag type
    set_tags_in_dict = list(
        dict.fromkeys([el.get("tag") for el in dict_label.values()])
    )

    first_embed = True
    for current_tag in set_tags_in_dict:
        # Build list of elements if it belongs to the tag
        list_label_to_display = [
            f"{label_module.read_tag(value.get('tag'))['discord_emoji']} **{key}** :arrow_right: {value.get('name')}"
            for key, value in dict_label.items()
            if value.get("tag") == current_tag
        ]

        # Build description and embed from it
        description = f":arrow_double_down: **Quêtes {label_module.read_tag(current_tag)['name']}**\n\n" + "\n\n".join(list_label_to_display)

        # display title on the first embed sent
        if first_embed:
            title = "Labels possible pour la commande `/ajout_quete <label>`"
        else:
            title = None
        embed = discord.Embed(title=title, description=description)
        await send_message_from_interaction(
            interaction=interaction,
            is_followup=not first_embed,
            msg=None,
            embed=embed
        )
        first_embed = False
        
 