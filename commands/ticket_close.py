# ticket/ticket_close.py
import discord
from discord import ui
import asyncio

class CloseConfirm(ui.View):
    def __init__(self):
        super().__init__(timeout=30)
    
    @ui.button(label="✅ Confirm Close", style=discord.ButtonStyle.danger)
    async def confirm_close(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("🗑️ Deleting ticket in 3 seconds...", ephemeral=True)
        await asyncio.sleep(3)
        
        try:
            await interaction.channel.delete(reason=f"Ticket closed by {interaction.user}")
        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to delete this channel!", ephemeral=True)
