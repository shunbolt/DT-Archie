import discord

# Modal for adding extra informations to the quests

class AddQuestModal(discord.ui.Modal, title="Informations supplémentaires"):
    
    commentary_input = discord.ui.Label(text="Commentaires", component=discord.ui.TextInput(
            style=discord.TextStyle.paragraph,
            placeholder="Ecrire un commentaire",
            required=False,
            max_length=1000
    )) 
    
    helper_checkbox =  discord.ui.Label(text="Passeur ?", component= discord.ui.Checkbox(
            default=False
        ))
    
    def __init__(self, parent_view: discord.ui.View):
        super().__init__(timeout=180)
        
        self.parent_view = parent_view 

        # Pre-fill modal with any existing data if re-opened
        if self.parent_view.commentary_text:
            self.commentary_input.component.default = self.parent_view.commentary_text
        
        self.helper_checkbox.component.default = True if self.parent_view.is_helper else False

    async def on_submit(self, interaction: discord.Interaction):
        # 1. Store commentary text
        self.parent_view.commentary_text = self.commentary_input.component.value.strip()

        # 2. Parse value in checkbox
        self.parent_view.is_helper = self.helper_checkbox.component.value

        # 3. Update the View message directly with the new details
        await interaction.response.edit_message(
            content="Mise à jour des informations avancées de la quête",
            view=self.parent_view
        )