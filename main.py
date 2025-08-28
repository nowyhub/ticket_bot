import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
BOT_PREFIX = os.getenv('BOT_PREFIX', '?')

if not DISCORD_BOT_TOKEN:
    print("ERROR: DISCORD_BOT_TOKEN not found in .env file!")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot prefix: {BOT_PREFIX}')
    print(f'Bot is in {len(bot.guilds)} guilds')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

async def load_commands_recursively(folder_path, prefix=""):
    """Recursively load all Python files from commands folder and subfolders."""
    if not os.path.exists(folder_path):
        return
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path) and not item.startswith('__'):
            new_prefix = f"{prefix}.{item}" if prefix else item
            await load_commands_recursively(item_path, new_prefix)
        elif item.endswith('.py') and not item.startswith('__'):
            try:
                module_name = f"{prefix}.{item[:-3]}" if prefix else item[:-3]
                await bot.load_extension(f'commands.{module_name}')
                print(f':white_check_mark: Loaded command: {module_name}')
            except Exception as e:
                print(f':x: Failed to load command {module_name}: {e}')

async def main():
    async with bot:
        await load_commands_recursively('commands')
        await bot.start(DISCORD_BOT_TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
