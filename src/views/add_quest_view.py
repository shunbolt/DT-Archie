from pickledb import PickleDB

import discord
from discord.ext import commands

from src.views.add_quest_modal import AddQuestModal
from src.response.discord_response import add_quest_to_database
from src.label import label_module


class AddQuestView(discord.ui.View):
    # Pass discord.User (or Member) into __init__
    def __init__(self, bot: commands.Bot, database : PickleDB):
        super().__init__(timeout=180)
        # External arguments from commands 
        self.bot = bot
        self.database = database
        
        # Initialized argument
        self.dict_label = None
        self.selected_tag = None
        self.selected_quest = None  
        
        # Modal attributes
        self.commentary_text = None
        self.is_helper = False
        
        # Read list of all labels
        self.dict_label = label_module.read_full_label()

        # Get set of different tags 
        set_tags_in_dict = list(
            dict.fromkeys([el.get("tag") for el in self.dict_label.values()])
        )
        
        # Create select for tag options
        tag_options = [
            discord.SelectOption(label=label_module.read_tag(current_tag).get('name'), value=current_tag)
            for current_tag in set_tags_in_dict
        ]
        
        self.tag_select = discord.ui.Select(
            placeholder="Etape 1: Choisis une tranche de niveau",
            options=tag_options,
            row=0
        )
        self.tag_select.callback = self.tag_callback
        self.add_item(self.tag_select)
        
        # Create select for quests options (disabled by default)
        self.quest_select = discord.ui.Select(
            placeholder="Etape 2: Choisis une quête",
            options=[discord.SelectOption(label="-", value="-")],
            disabled=True,
            row=1
        )
        self.quest_select.callback = self.quest_callback
        self.add_item(self.quest_select)
        
        # Create open extra settings button (disabled if no quest selected)
        self.settings_button = discord.ui.Button(
            label="Paramètres supplémentaires",
            style=discord.ButtonStyle.secondary,
            emoji="⚙️",
            disabled=True,
            row=2
        )
        self.settings_button.callback = self.settings_callback
        self.add_item(self.settings_button)
        
        # Create publish button (disabled if no quest selected)
        self.publish_button = discord.ui.Button(
            label="Publier la quête",
            style=discord.ButtonStyle.primary,
            emoji="📜",
            disabled=True,
            row=2
        )
        self.publish_button.callback = self.publish_callback
        self.add_item(self.publish_button)    

    async def tag_callback(self, interaction: discord.Interaction):
        """Callback when choosing a tag in the select tag option
        """
        # Update current active tag and reset item choice
        self.selected_tag = self.tag_select.values[0]
        self.selected_quest = None
        
        # Get tag name from list of tag labels
        tag_name = label_module.read_tag(self.selected_tag).get("name")
        
        # Set the selected tag as default to let it persist after view refresh
        for option in self.tag_select.options:
            option.default = (option.value == self.selected_tag)
        
        # Rebuild the quests dropdown options from the selected tag
        new_quests_options = [
            discord.SelectOption(
                label=value.get('name'),  # Label to display
                value=key,               # Value to return
                description=label_module.read_category(value.get('category'))['name']   # Description 
            )
            for key, value in self.dict_label.items()
            if value.get("tag") == self.selected_tag
        ][:25] # Max 25 items per category

        # Update the item dropdown state
        self.quest_select.options = new_quests_options
        self.quest_select.placeholder = f"Etape 2: Choisis une quête de niveau '{tag_name}'..."
        self.quest_select.disabled = False

        # Refresh the UI message
        await interaction.response.edit_message(
            content=f"Tranche de niveau choisi : **{tag_name}**. Sélectionnes une quête ci-dessous:",
            view=self
        )

    async def quest_callback(self, interaction: discord.Interaction):
        """Callback when selecting a quest
        """
        self.selected_quest = self.quest_select.values[0]
        
        # Update buttons
        self.publish_button.disabled = False
        self.settings_button.disabled = False
        self.publish_button.style = discord.ButtonStyle.success
        
        # Get the name of the quest 
        self.quest_name = label_module.read_label(self.selected_quest).get("name")
        
        # Set the selected quest as default to let it persist after view refresh
        for option in self.quest_select.options:
            option.default = (option.value == self.selected_quest)
        
        await interaction.response.edit_message(
            content=f"Quête sélectionnée : **{self.quest_name}** prête à être publiée. Cliques sur le bouton 'Publier la quête'",
            view=self
    )
        
    async def settings_callback(self, interaction: discord.Interaction):
        # Open the modal 
        await interaction.response.send_modal(AddQuestModal(parent_view=self))
        

    async def publish_callback(self, interaction: discord.Interaction):
        # If no quest is selected, display an error message
        if not self.selected_quest:
            await interaction.response.edit_message(
                content=":warning: Sélectionnes d'abord une catégorie et une quête depuis le formulaire",
                view=self
            )
            return

        # Disable all components after publishing
        for child in self.children:
            child.disabled = True

        # Update the original response to show disabled buttons and confirm
        await interaction.response.edit_message(
            content=f":white_check_mark: Quête **{self.quest_name}** publiée avec succès !",
            view=self
        )
        
        # Add the quest from the view form to the database
        await add_quest_to_database(
            bot=self.bot,
            interaction=interaction,
            database=self.database,
            quest_label=self.selected_quest,
            quest_comments=self.commentary_text,
            is_helper=self.is_helper,
            is_followup=True
        )
        
        self.stop()

