# ticket/ticket_controls.py
import discord
from discord import ui, utils

def load_module_from_path(module_name, file_path):
    import importlib.util
    import sys
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

class TicketControls(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @ui.button(label="🗃️ Archive", style=discord.ButtonStyle.secondary, custom_id="archive_ticket")
    async def archive_ticket(self, interaction: discord.Interaction, button: ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            # Check if user has staff role
            staff_role = utils.get(interaction.guild.roles, name="Staff")
            if not staff_role:
                staff_role = utils.get(interaction.guild.roles, name="Support")
            if not staff_role:
                staff_role = utils.get(interaction.guild.roles, name="Moderator")
            if not staff_role:
                staff_role = utils.get(interaction.guild.roles, name="Admin")
                
            if not staff_role or staff_role not in interaction.user.roles:
                return await interaction.response.send_message("❌ You don't have permission to archive tickets!", ephemeral=True)
        
        # Load archive module
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        archive_path = os.path.join(current_dir, "ticket_archive.py")
        archive_module = load_module_from_path("ticket_archive", archive_path)
        ArchiveConfirm = archive_module.ArchiveConfirm
        
        embed = discord.Embed(
            title="⚠️ Archive Ticket",
            description="Are you sure you want to archive this ticket?",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, view=ArchiveConfirm(), ephemeral=True)
    
    @ui.button(label="🗑️ Close", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            # Check if user has staff role
            staff_role = utils.get(interaction.guild.roles, name="Staff")
            if not staff_role:
                staff_role = utils.get(interaction.guild.roles, name="Support")
            if not staff_role:
                staff_role = utils.get(interaction.guild.roles, name="Moderator")
            if not staff_role:
                staff_role = utils.get(interaction.guild.roles, name="Admin")
                
            if not staff_role or staff_role not in interaction.user.roles:
                return await interaction.response.send_message("❌ You don't have permission to close tickets!", ephemeral=True)
        
        # Load close module
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        close_path = os.path.join(current_dir, "ticket_close.py")
        close_module = load_module_from_path("ticket_close", close_path)
        CloseConfirm = close_module.CloseConfirm
        
        embed = discord.Embed(
            title="⚠️ Close Ticket",
            description="Are you sure you want to close this ticket? This action cannot be undone!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, view=CloseConfirm(), ephemeral=True)
    
    @ui.button(label="📋 Transcript", style=discord.ButtonStyle.primary, custom_id="transcript_ticket")
    async def create_transcript(self, interaction: discord.Interaction, button: ui.Button):
        # Load transcript module
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        transcript_path = os.path.join(current_dir, "ticket_transcript.py")
        transcript_module = load_module_from_path("ticket_transcript", transcript_path)
        generate_transcript = transcript_module.generate_transcript
        
        await generate_transcript(interaction)