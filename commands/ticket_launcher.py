# ticket/ticket_launcher.py
import discord
from discord import ui, utils
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

# Load the modules
ticket_modal_path = os.path.join(current_dir, "ticket_modal.py")
ticket_controls_path = os.path.join(current_dir, "ticket_controls.py")

ticket_modal_module = load_module_from_path("ticket_modal", ticket_modal_path)
ticket_controls_module = load_module_from_path("ticket_controls", ticket_controls_path)

TicketModal = ticket_modal_module.TicketModal
TicketControls = ticket_controls_module.TicketControls

class TicketLauncher(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="📩 Create Ticket", style=discord.ButtonStyle.green, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: ui.Button):
        # Check if user already has a ticket
        for channel in interaction.guild.text_channels:
            if channel.name.startswith("ticket-") and str(interaction.user.id) in channel.name:
                return await interaction.response.send_message(f"❌ You already have a ticket open: {channel.mention}", ephemeral=True)
        
        # Get the next ticket number
        ticket_number = 1
        for channel in interaction.guild.text_channels:
            if channel.name.startswith("ticket-"):
                try:
                    # Extract number from channel name like "ticket-5-username"
                    parts = channel.name.split("-")
                    if len(parts) >= 2 and parts[1].isdigit():
                        current_num = int(parts[1])
                        if current_num >= ticket_number:
                            ticket_number = current_num + 1
                except:
                    continue
        
        # Set up permissions
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True, 
                send_messages=True, 
                read_message_history=True,
                attach_files=True,
                embed_links=True
            ),
            interaction.guild.me: discord.PermissionOverwrite(
                view_channel=True, 
                send_messages=True, 
                read_message_history=True,
                manage_channels=True,
                manage_messages=True
            )
        }
        
        # Add staff role if it exists
        staff_role = utils.get(interaction.guild.roles, name="Staff")
        if not staff_role:
            staff_role = utils.get(interaction.guild.roles, name="Support")
        if not staff_role:
            staff_role = utils.get(interaction.guild.roles, name="Moderator")
        if not staff_role:
            staff_role = utils.get(interaction.guild.roles, name="Admin")
            
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                manage_messages=True
            )
        
        # Get or create tickets category
        category = utils.get(interaction.guild.categories, name="🎫┃Tickets")
        if not category:
            try:
                category = await interaction.guild.create_category("🎫┃Tickets")
            except discord.Forbidden:
                return await interaction.response.send_message("❌ I don't have permission to create categories!", ephemeral=True)
        
        # Create ticket channel
        try:
            channel_name = f"ticket-{ticket_number}-{interaction.user.name}".lower().replace(" ", "-")
            ticket_channel = await interaction.guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites,
                reason=f"Ticket #{ticket_number} for {interaction.user}"
            )
            
            # Send the modal
            await interaction.response.send_modal(TicketModal(ticket_channel))
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to create channels! Make sure I have `Manage Channels` permission.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error creating ticket: {str(e)}", ephemeral=True)