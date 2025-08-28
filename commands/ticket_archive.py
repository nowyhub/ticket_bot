# ticket/ticket_archive.py
import discord
from discord import ui, utils
from datetime import datetime
import asyncio

class ArchiveConfirm(ui.View):
    def __init__(self):
        super().__init__(timeout=30)
    
    @ui.button(label="✅ Confirm Archive", style=discord.ButtonStyle.secondary)
    async def confirm_archive(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("🗃️ Archiving ticket in 3 seconds...", ephemeral=True)
        await asyncio.sleep(3)
        
        # Get or create archive category
        archive_category = utils.get(interaction.guild.categories, name="📁┃Archives")
        if not archive_category:
            try:
                archive_category = await interaction.guild.create_category("📁┃Archives")
            except discord.Forbidden:
                return await interaction.followup.send("❌ Cannot create archive category!", ephemeral=True)
        
        try:
            # Move channel to archive category and rename
            new_name = f"archived-{interaction.channel.name}"
            await interaction.channel.edit(name=new_name, category=archive_category)
            
            # Remove user permissions
            original_user = None
            for member in interaction.guild.members:
                if str(member.id) in interaction.channel.name:
                    original_user = member
                    break
            
            if original_user:
                await interaction.channel.set_permissions(original_user, overwrite=None)
            
            embed = discord.Embed(
                title="🗃️ Ticket Archived",
                description=f"This ticket has been archived by {interaction.user.mention}",
                color=discord.Color.orange(),
                timestamp=datetime.now()
            )
            await interaction.channel.send(embed=embed)
            
        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to archive this ticket!", ephemeral=True)