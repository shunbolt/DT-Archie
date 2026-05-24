import discord
from discord import app_commands
from discord.ext import commands
from pickledb import PickleDB

from src.database import database_module
from src.label import label_module


def bot_commands(bot: commands.Bot, database: PickleDB):
    """
    Function to register all bot commands

    Args:
        bot (commands.Bot): Discord bot instance
        database (PickleDB): PickleDB database for storing and querying data
    """

    # Subfunctions
    # Display embed of quests from member
    def embed_quest_list_from_member(
        member: discord.member, list_quests: list, hide_index=False
    ) -> discord.Embed:
        """Subfunction to build the embed message of the list of quests from a member

        Args:
            member (discord.member): Discord member to display quests from
            list_quests (list): List of it's quests from the data
            hide_index (bool): boolean to hide index value for embed. Defaults to false
        """
        # Build embed with the quests information
        embed = discord.Embed(
            title=f"Quêtes de {member.display_name} sur le comptoir de quêtes de la guilde :"
        )
        embed.set_thumbnail(url=member.avatar.url)

        for index, quest in enumerate(list_quests):
            # Get index for the quest
            if hide_index:
                quest_index = ""
            else:
                quest_index = f"#{index + 1}"
                
            # Get helper value
            quest_helper_flag = quest.get("helper_flag")

            # Adjust quest_prefix based on helper flag value
            if quest_helper_flag:
                quest_prefix = ":star2: :star2: :star2: Assistant de quête"
            else:
                quest_prefix = "Quête"

            # Get quest components to display
            quest_category = label_module.read_category(quest["quest_category"])
            quest_category_name = quest_category["name"]
            quest_category_emoji = quest_category["discord_emoji"]
            quest_label = label_module.read_label(quest["quest_label"])["name"]
            quest_comments = quest["quest_comments"]

            # Add emoji based on difficulty tag : implement on a dict directly
            quest_tag = label_module.read_label(quest["quest_label"])["tag"]
            quest_tag_name = label_module.read_tag(quest_tag)["name"]
            quest_tag_emoji = label_module.read_tag(quest_tag)["discord_emoji"]

            embed_name = f"{quest_category_emoji} {quest_prefix} {quest_category_name} {quest_tag_name} {quest_index}"

            embed.add_field(
                name=embed_name,
                value=f""":label: Nom : {quest_label} {quest_tag_emoji}\n:pencil: Commentaires : {quest_comments}""",
                inline=False,
            )

        return embed

    # Check if the selected label belongs to the dict and send message to relevant members
    async def mention_common_members(
        interaction: discord.Interaction, quest_label=None
    ):
        """Get the lists of members having the specified label quests in their list and mentions them in a message

        Args:
            ctx (commands.Context): discord context of the command
            quest_label (_type_, optional): quest label to search for. Defaults to None.
        """
        server_id = str(interaction.guild.id)

        if quest_label:
            dict_users_quests = await database_module.get_quests_from_server(
                database=database, server_id=server_id, filter_label=quest_label
            )

            # Get the list of members id with common members except yourself
            list_members_id = [
                user_id
                for user_id in dict_users_quests.keys()
                if user_id != str(interaction.user.id)
            ]
            
            helper_members_id = [
                user_id
                for user_id in dict_users_quests.keys()
                if user_id != str(interaction.user.id) and any([el.get("helper_flag") for el in dict_users_quests[user_id]])
            ]

            for member_id in list_members_id:
                member = bot.get_guild(int(server_id)).get_member(int(member_id))
                
                if member_id in helper_members_id:
                    message = f":sparkles: Mercenaire {member.mention} est un assistant qui peut t'aider à accomplir ta quête !"
                else:
                    message = f":dart: Mercenaire {member.mention} partage la même quête que toi et peut t'aider !"
                
                await interaction.followup.send(content=message)

    # Archie commands
    # Command to insert a quest to the database
    @bot.tree.command(name="ajout_quete", description="Ajoute une quête à ton nom")
    @app_commands.rename(quest_label='label_quête', quest_comments='commentaires', helper_flag='assistance')
    @app_commands.describe(
        quest_label="Libellé de quête", quest_comments="Commentaires optionnels", helper_flag="Se porter volontaire en tant qu'assistant/passeur"
    )
    async def ajout_quete(
        interaction: discord.Interaction,
        quest_label: str = None,
        quest_comments: str = "",
        helper_flag: str = "False"
    ):
        """Command to add a quest to the billboard

        Args:
            ctx (discord.Context): discord context of the command
            quest_label (str): Argument corresponding to the quest label
            If help label is passed, display the list of all possible labels and bosses
            quest_comments (str): Argument corresponding to the comments. Defaults to None
            helper_flag (bool): Argument to determine if the quest added is as a helper. Defaults to False
        """
        # Define help labels
        help_labels = ["help", "aide", None]

        # Get credentials from the discord context
        server_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        server_name = interaction.guild.name
        user_name = interaction.user.display_name
        
        # Convert helper flag
        if(helper_flag=="True"):
            helper_flag=True
        else:
            helper_flag=False

        if quest_label in help_labels:
            # Read list of all labels
            dict_label = label_module.read_full_label()

            # Get list of different tag type
            set_tags_in_dict = list(
                dict.fromkeys([el.get("tag") for el in dict_label.values()])
            )

            first_embed = True
            embed_list = []
            for current_tag in set_tags_in_dict:
                # Build list of elements if it belongs to the tag
                list_label_to_display = [
                    f"{label_module.read_tag(value.get('tag'))['discord_emoji']} **{key}** :arrow_right: {value.get('name')}"
                    for key, value in dict_label.items()
                    if value.get("tag") == current_tag
                ]

                # Build description and embed from it
                description = "\n\n".join(list_label_to_display)

                # display title on the first embed sent
                if first_embed:
                    title = "Labels possible pour la commande `!ajout_quete <label>`"
                    first_embed = False
                else:
                    title = None
                embed = discord.Embed(title=title, description=description)

                embed_list.append(embed)

            await interaction.response.send_message(embeds=embed_list)
        else:
            # Read category based on label name
            label_dict = label_module.read_label(quest_label)

            if label_dict is not None:
                quest_category = label_dict["category"]

                quest_dict = {
                    "server_name": server_name,
                    "user_name": user_name,
                    "quest_category": quest_category,
                    "quest_label": quest_label,
                    "quest_comments": quest_comments,
                    "helper_flag": helper_flag
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
                    helper_flag=helper_flag
                )

                quest_embed = embed_quest_list_from_member(
                    interaction.user, [quest_dict], hide_index=True
                )
                
                if helper_flag:
                    await interaction.response.send_message(
                        content=f":raised_hand: Mercenaire {interaction.user.mention} s'est porté volontaire comme assistant à la quête suivante :",
                        embed=quest_embed,
                    )
                else:
                    await interaction.response.send_message(
                        content=f":bell: Mercenaire {interaction.user.mention} a ajouté la quête suivante sur le comptoir de quêtes de la guilde :",
                        embed=quest_embed,
                    )

                # Mention members that have the same label
                await mention_common_members(
                    interaction=interaction, quest_label=quest_label
                )

            else:
                await interaction.response.send_message(
                    content=f"""Aucune quête n'a été trouvée avec le libellé : {quest_label}"""
                )

    # Command to get all quests from the current user
    @bot.tree.command(
        name="lire_quetes",
        description="Affiches l'ensemble de tes quêtes ordonnée par indices",
    )
    async def lire_quetes(interaction: discord.Interaction):
        """Function to read quests. Nest the logic

        Args:
            interaction (discord.Interaction): Discord interaction context
        """
        await lire_quetes_logic(interaction=interaction)

    async def lire_quetes_logic(interaction: discord.Interaction, followup=False):
        """Logic computation to read quests from the user on the quest billboard

        Args:
            interaction (discord.Interaction): Discord interaction context
            followup (bool) : Boolean to determine if the logic is called as followup or not
        """
        # Get credentials from the discord context
        server_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)

        list_quests = await database_module.get_quests_from_user(
            database=database, server_id=server_id, user_id=user_id
        )

        if list_quests:
            # Get the list of quests into an embed
            embed = embed_quest_list_from_member(
                member=interaction.user, list_quests=list_quests
            )

            if followup:
                await interaction.followup.send(embed=embed)
            else:
                await interaction.response.send_message(embed=embed)
        else:
            msg = "Il n'y a aucune quête à ton nom sur le comptoir : utilise `/ajout_quete` pour en ajouter une!"
            if followup:
                await interaction.followup.send(
                    content=msg
                )
            else:
                await interaction.response.send_message(
                    content=msg
                )

    # Command to get all quests from the current server
    @bot.tree.command(
        name="lire_toutes_quetes",
        description="Affiches l'ensemble des quêtes de tous les membres du serveur",
    )
    @app_commands.rename(quest_label='label_quête')
    @app_commands.describe(quest_label="Libellé de quête")
    async def lire_toutes_quetes(
        interaction: discord.Interaction, quest_label: str = None
    ):
        """Function to read all quests from the server

        Args:
            interaction (discord.Interaction): Discord interaction context
            quest_label (str): first optional argument corresponding to the label to filter
        """
        # Get credentials from the discord context
        server_id = str(interaction.guild.id)

        dict_users_quests = await database_module.get_quests_from_server(
            database=database, server_id=server_id, filter_label=quest_label
        )

        # If dict is not empty
        if dict_users_quests:
            # List all users into a string
            list_user_name = ", ".join(
                [
                    bot.get_guild(int(server_id)).get_member(int(user_id)).display_name
                    for user_id in dict_users_quests.keys()
                ]
            )

            await interaction.response.send_message(
                content=f"La liste des membres ayant renseigné une quête sur le comptoir est la suivante : {list_user_name}"
            )

            # Build embed for each user with their quests
            for user_id, quest_list in dict_users_quests.items():
                embed = embed_quest_list_from_member(
                    bot.get_guild(int(server_id)).get_member(int(user_id)), quest_list
                )

                await interaction.followup.send(embed=embed)

            await mention_common_members(
                interaction=interaction, quest_label=quest_label
            )
        else:
            if quest_label:
                # Message if there is no quest for the selected label
                await interaction.response.send_message(
                    content="Il n'y a aucune quête de ce type sur le comptoir : utilise `/ajout_quete` pour en ajouter une!"
                )
            else:
                # Message if there is no quest at all
                await interaction.response.send_message(
                    content="Il n'y a aucune quête sur le comptoir : utilise `/ajout_quete` pour être le premier à en ajouter!"
                )

    # Command to remove a quest from the user list
    @bot.tree.command(
        name="supp_quete",
        description="Supprimes la quête indexé en argument de ta liste de quête",
    )
    @app_commands.rename(idx="quete_supprimer")
    @app_commands.describe(idx="Index de la liste de quête")
    async def supp_quete(interaction: discord.Interaction, idx: int):
        """Function to remove a quest given it's displayed index (offset by 1)

        Args:
            interaction (discord.Interaction): Discord interaction context
            arg : argument expecting an index
        """

        # Get credentials from the discord context
        server_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)

        if isinstance(idx, int):
            list_index = idx - 1

            quest_label_removed = await database_module.remove_quest_from_index(
                database=database, server_id=server_id, user_id=user_id, idx=list_index
            )

            if quest_label_removed:
                await interaction.response.send_message(
                    f"La quête de {interaction.user.display_name} - {label_module.read_label(quest_label_removed)['name']} numérotée #{idx} a été correctement supprimée"
                )
                await lire_quetes_logic(interaction=interaction, followup=True)
            else:
                await interaction.response.send_message(
                    f"La quête de {interaction.user.display_name} numérotée {idx} n'est pas trouvable"
                )
        else:
            await interaction.response.send_message(
                "Numéro d'index inconnu on non reconnu : veuillez réessayer"
            )

    # Comment to get help
    @bot.tree.command(
        name="aide", description="Fonction pour afficher le guide d'utilisation"
    )
    async def aide(interaction: discord.Interaction):
        """Function to display the help text

        Args:
            ctx (commands.Context): discord context of the command
        """

        await interaction.response.send_message(
            content=label_module.read_help(help_type="/")
        )

    # Autocomplete logic

    @ajout_quete.autocomplete("quest_label")
    @lire_toutes_quetes.autocomplete("quest_label")
    async def quest_label_autocomplete(interaction: discord.Interaction, current: str):
        """Autocomplete decorator function for selecting a quest label

        Args:
            interaction (discord.Interaction): Discord interaction context
            current (str): Current string being typed
        """

        dict_label = label_module.read_full_label()

        list_labels = [
            {"key": key, "name": value.get("name")} for key, value in dict_label.items()
        ]

        return [
            app_commands.Choice(
                name=f"{choice.get('key')} - {choice.get('name')}",
                value=choice.get("key"),
            )
            for choice in list_labels
            if current.lower() in f"{choice.get('key')} - {choice.get('name')}".lower()
        ][:25]
        
    @ajout_quete.autocomplete("helper_flag")
    async def true_false_autocomplete(interaction: discord.Interaction, current: str):
        """Autocomplete decorator function for true/false parameter

        Args:
            interaction (discord.Interaction): Discord interaction context
            current (str): Current string being typed
        """

        bool_dict = {   
                        "Oui": "True", 
                        "Non": "False" 
                    }

        return [
            app_commands.Choice(
                name=choice,
                value=bool_dict.get(choice),
            )
            for choice in bool_dict
            if current.lower() in choice.lower()
        ]

    @supp_quete.autocomplete("idx")
    async def quest_delete_idx_autocomplete(
        interaction: discord.Interaction, current: str
    ):
        """Autocomplete decorator function for selecting the quest of the current user

        Args:
            interaction (discord.Interaction): Discord interaction context
            current (str): Current string being typed
        """
        # Get credentials from the discord context
        server_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)

        list_quests = await database_module.get_quests_from_user(
            database=database, server_id=server_id, user_id=user_id
        )

        list_labels_quests = [
            {
                "index": index + 1,
                "name": label_module.read_label(quest["quest_label"])["name"],
                "comments": quest["quest_comments"],
            }
            for index, quest in enumerate(list_quests)
        ]

        return [
            app_commands.Choice(
                name=f"#{choice.get('index')} - {choice.get('name')} {choice.get('comments')}",
                value=choice.get("index"),
            )
            for choice in list_labels_quests
            if current.lower() in f"{choice.get('name')}".lower()
        ][:25]
