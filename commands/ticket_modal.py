# ticket/ticket_modal.py
import discord
from discord import ui
from datetime import datetime

class TicketModal(ui.Modal, title="Create Ticket"):
    issue = ui.TextInput(
        label="What is your issue?", 
        style=discord.TextStyle.paragraph, 
        placeholder="Describe your issue here...", 
        required=True, 
        max_length=1000
    )
    
    def __init__(self, ticket_channel):
        super().__init__()
        self.ticket_channel = ticket_channel
    
    async def on_submit(self, interaction: discord.Interaction):
        # Load controls module dynamically
        import importlib.util
        import sys
        import os
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        controls_path = os.path.join(current_dir, "ticket_controls.py")
        
        spec = importlib.util.spec_from_file_location("ticket_controls", controls_path)
        controls_module = importlib.util.module_from_spec(spec)
        sys.modules["ticket_controls"] = controls_module
        spec.loader.exec_module(controls_module)
        
        TicketControls = controls_module.TicketControls
        
        embed = discord.Embed(
            title="New Ticket Issue", 
            description=self.issue.value, 
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"Ticket created by {interaction.user}")
        
        await self.ticket_channel.send(f"{interaction.user.mention} created a ticket!", embed=embed, view=TicketControls())
        await interaction.response.send_message(f"✅ Your ticket has been created at {self.ticket_channel.mention}!", ephemeral=True)