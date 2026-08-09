import os

import discord
from discord import app_commands
from discord.ext import commands
from pickledb import PickleDB

from src.database import database_module
from src.label import label_module
from src.views.add_quest_view import AddQuestView
from src.response.discord_response import embed_quest_list_from_member, mention_common_members, display_labels, add_quest_to_database

SCRIPT_PATH = os.path.dirname(__file__)

def bot_commands(bot: commands.Bot, database: PickleDB):
    """
    Function to register all bot commands

    Args:
        bot (commands.Bot): Discord bot instance
        database (PickleDB): PickleDB database for storing and querying data
    """
                
    # Archie commands
    # Command to insert a quest to the database
    @bot.tree.command(name="ajout_quete", description="Ajoute une quête à ton nom")
    @app_commands.rename(quest_label='label_quête', quest_comments='commentaires', helper_flag='assistance')
    @app_commands.describe(
        quest_label="Libellé de quête", quest_comments="Commentaires optionnels", helper_flag="Se porter volontaire en tant que passeur"
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
        # Define none values
        none_labels = ["help", "aide", " ", "", None]

        if quest_label in none_labels:
            view = AddQuestView(bot=bot, database=database)
            await interaction.response.send_message(view=view, ephemeral=True)
        else:
            
            # Convert helper flag
            if(helper_flag=="True"):
                helper_flag=True
            else:
                helper_flag=False
                
            await add_quest_to_database(
                bot=bot,
                interaction=interaction,
                database=database,
                quest_label=quest_label,
                quest_comments=quest_comments,
                is_helper=helper_flag,
                is_followup=False
            )

    # Command to get all quests from the current user
    @bot.tree.command(
        name="lire_quetes",
        description="Affiches l'ensemble de tes quêtes ordonnée par indices",
    )
    @app_commands.rename(ephemeral='privée')
    @app_commands.describe(ephemeral="Afficher la réponse en privée dans le canal")
    async def lire_quetes(interaction: discord.Interaction, ephemeral : str = "False"):
        """Function to read quests. Nest the logic

        Args:
            interaction (discord.Interaction): Discord interaction context
            ephemeral (bool): Argument to determine if response should be ephemeral or not
        """
        
        # Convert ephemeral flag
        if(ephemeral=="True"):
            ephemeral=True
        else:
            ephemeral=False
        
        await lire_quetes_logic(interaction=interaction, ephemeral=ephemeral, followup=False)

    async def lire_quetes_logic(interaction: discord.Interaction, ephemeral=False, followup=False):
        """Logic computation to read quests from the user on the quest billboard

        Args:
            interaction (discord.Interaction): Discord interaction context
            ephemeral (bool) : Boolean to determine if message should be ephemeral 
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
                await interaction.followup.send(embed=embed, ephemeral=ephemeral)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
        else:
            msg = "Il n'y a aucune quête à ton nom sur le comptoir : utilise `/ajout_quete` pour en ajouter une!"
            if followup:
                await interaction.followup.send(
                    content=msg,
                    ephemeral=ephemeral
                )
            else:
                await interaction.response.send_message(
                    content=msg,
                    ephemeral=ephemeral
                )

    # Command to get all quests from the current server
    @bot.tree.command(
        name="lire_toutes_quetes",
        description="Affiches l'ensemble des quêtes de tous les membres du serveur",
    )
    @app_commands.rename(quest_label='label_quête', ephemeral='privée')
    @app_commands.describe(quest_label="Libellé de quête", ephemeral="Afficher la réponse en privée dans le canal")
    async def lire_toutes_quetes(
        interaction: discord.Interaction, quest_label: str = None, ephemeral : str = "False",
    ):
        """Function to read all quests from the server

        Args:
            interaction (discord.Interaction): Discord interaction context
            quest_label (str): first optional argument corresponding to the label to filter
            ephemeral (bool): Argument to determine if response should be ephemeral or not
        """
        # Get credentials from the discord context
        server_id = str(interaction.guild.id)
        
        # Convert ephemeral flag
        if(ephemeral=="True"):
            ephemeral=True
        else:
            ephemeral=False

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
                content=f"La liste des membres ayant renseigné une quête sur le comptoir est la suivante : {list_user_name}",
                ephemeral=ephemeral
            )

            # Build embed for each user with their quests
            for user_id, quest_list in dict_users_quests.items():
                embed = embed_quest_list_from_member(
                    bot.get_guild(int(server_id)).get_member(int(user_id)), quest_list
                )

                await interaction.followup.send(embed=embed, ephemeral=ephemeral)

            if not ephemeral:
                await mention_common_members(
                   bot=bot, interaction=interaction, database=database, quest_label=quest_label
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
                await lire_quetes_logic(interaction=interaction, ephemeral=True, followup=True)
            else:
                await interaction.response.send_message(
                    f"La quête de {interaction.user.display_name} numérotée {idx} n'est pas trouvable"
                )
        else:
            await interaction.response.send_message(
                "Numéro d'index inconnu on non reconnu : veuillez réessayer"
            )

    # Command to get help
    @bot.tree.command(
        name="aide", description="Commande pour afficher le guide d'utilisation du bot"
    )
    async def aide(interaction: discord.Interaction):
        """Function to display the help text

        Args:
            interaction (discord.Interaction): discord context of the command
        """

        await interaction.response.send_message(
            content=label_module.read_help(help_type="/")
        )
        
    # Command to get help through gifs
    @bot.tree.command(
        name="aide_gifs", description="Commande pour afficher via des gifs l'utilisation du bot"
    )
    async def aide_gifs(interaction: discord.Interaction):
        """Function to display help with gifs

        Args:
            interaction (discord.Interaction): discord context of the command
        """
        # HACK : Put paths into dedicated file
        PATH_GIF_ADD_QUEST = os.path.join(SCRIPT_PATH, "../..", "static", "gifs", "archie_add_quest.gif")
        PATH_GIF_ADD_ASSIST = os.path.join(SCRIPT_PATH, "../..", "static", "gifs", "archie_add_assist.gif")
        PATH_GIF_REMOVE_QUEST = os.path.join(SCRIPT_PATH, "../..", "static", "gifs", "archie_remove_quest.gif")

        dict_gifs = {
            "add_quest" : 
                { 
                 "path" : PATH_GIF_ADD_QUEST,
                 "msg" : "Comment ajouter une quête dans le comptoir de guilde :"
                },
            "add_assist" :
                { 
                 "path" : PATH_GIF_ADD_ASSIST,
                 "msg" : "Comment devenir passeur pour un donjon + mention auprès d'un membre :"
                },
            "remove_quest" : 
                { 
                 "path" : PATH_GIF_REMOVE_QUEST,
                 "msg" : "Comment lire sa liste de quêtes et supprimer une quête spécifique (e.g : après l'avoir terminé ou reroll)"
                }
        }

        await interaction.response.send_message(content="Instructions vidéos ci-dessous :")
        for dict_content in dict_gifs.values():
            with open (dict_content["path"], 'rb') as gif_file :
                # Send gif message
                await interaction.followup.send(content=dict_content["msg"], file=discord.File(gif_file))
                
    @bot.tree.command(
        name="aide_quetes_libelles", description="Commande pour afficher tous les libellés de quêtes possibles"
    )
    async def aide_quetes_libelles(interaction: discord.Interaction):
        """Function to display all existing labels

        Args:
            interaction (discord.Interaction): discord context of the command
        """
        await display_labels(interaction=interaction)

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
    @lire_quetes.autocomplete("ephemeral")
    @lire_toutes_quetes.autocomplete("ephemeral")
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
