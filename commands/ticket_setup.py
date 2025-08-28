# ticket/ticket_setup.py
import discord
from discord.ext import commands
from discord import app_commands
import importlib.util
import sys
import os

def load_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Load the ticket launcher module
ticket_launcher_path = os.path.join(current_dir, "ticket_launcher.py")
ticket_launcher_module = load_module_from_path("ticket_launcher", ticket_launcher_path)
TicketLauncher = ticket_launcher_module.TicketLauncher

class TicketSetup(commands.GroupCog, name="ticket"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("✅ Ticket system is online!")

    @app_commands.command(name="setup", description="Set up the ticket system")
    @app_commands.default_permissions(manage_guild=True)
    async def setup_tickets(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎫 Support Tickets",
            description="Need help? Click the button below to create a support ticket!\n\n**How it works:**\n• Click the button to create a private ticket\n• Describe your issue\n• Wait for staff to help you\n• Your ticket will be numbered automatically",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Ticket System | Click the button below")
        
        await interaction.response.send_message("✅ Ticket system has been set up!", ephemeral=True)
        await interaction.channel.send(embed=embed, view=TicketLauncher())

    @app_commands.command(name="close", description="Close the current ticket")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def close_ticket(self, interaction: discord.Interaction):
        # Load close module dynamically
        close_path = os.path.join(current_dir, "ticket_close.py")
        close_module = load_module_from_path("ticket_close", close_path)
        CloseConfirm = close_module.CloseConfirm
        
        if not interaction.channel.name.startswith("ticket-"):
            return await interaction.response.send_message("❌ This command can only be used in ticket channels!", ephemeral=True)
        
        embed = discord.Embed(
            title="⚠️ Close Ticket",
            description="Are you sure you want to close this ticket?",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, view=CloseConfirm(), ephemeral=True)

    @app_commands.command(name="archive", description="Archive the current ticket")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def archive_ticket(self, interaction: discord.Interaction):
        # Load archive module dynamically
        archive_path = os.path.join(current_dir, "ticket_archive.py")
        archive_module = load_module_from_path("ticket_archive", archive_path)
        ArchiveConfirm = archive_module.ArchiveConfirm
        
        if not interaction.channel.name.startswith("ticket-"):
            return await interaction.response.send_message("❌ This command can only be used in ticket channels!", ephemeral=True)
        
        embed = discord.Embed(
            title="⚠️ Archive Ticket",
            description="Are you sure you want to archive this ticket?",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, view=ArchiveConfirm(), ephemeral=True)

    @app_commands.command(name="add", description="Add a user to the ticket")
    @app_commands.describe(user="The user to add to the ticket")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def add_user(self, interaction: discord.Interaction, user: discord.Member):
        if not interaction.channel.name.startswith("ticket-"):
            return await interaction.response.send_message("❌ This command can only be used in ticket channels!", ephemeral=True)
        
        try:
            await interaction.channel.set_permissions(
                user,
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                attach_files=True
            )
            await interaction.response.send_message(f"✅ {user.mention} has been added to this ticket!")
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to modify channel permissions!", ephemeral=True)

    @app_commands.command(name="remove", description="Remove a user from the ticket")
    @app_commands.describe(user="The user to remove from the ticket")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def remove_user(self, interaction: discord.Interaction, user: discord.Member):
        if not interaction.channel.name.startswith("ticket-"):
            return await interaction.response.send_message("❌ This command can only be used in ticket channels!", ephemeral=True)
        
        try:
            await interaction.channel.set_permissions(user, overwrite=None)
            await interaction.response.send_message(f"✅ {user.mention} has been removed from this ticket!")
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to modify channel permissions!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketSetup(bot))