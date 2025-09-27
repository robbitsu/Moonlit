import discord
from discord.ext import commands
from discord.app_commands import AppCommandContext
from dotenv import load_dotenv
import os

load_dotenv()

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True

owner = os.getenv('OWNER')

bot = commands.Bot(command_prefix='!', intents=intents, allowed_contexts=AppCommandContext(guild=True, dm_channel=False, private_channel=False), owner_id=owner)

bot.moon_phase: str = ""

async def load_cogs():
    for file in os.listdir('./cogs'):
        if file.endswith('.py'):
            await bot.load_extension(f'cogs.{file[:-3]}')
            print(f'Loaded cog: {file[:-3]}')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    await load_cogs()
    await bot.tree.sync()

@bot.command(name='ping')
async def ping(ctx):
    """Check if the bot is responsive"""
    await ctx.send('Pong!')

@bot.command(name='sync')
@commands.is_owner()
async def sync(ctx):
    """Sync the bot's commands"""
    await bot.tree.sync()
    await ctx.send('Commands synced!')

@bot.command(name='reload')
@commands.is_owner()
async def reload(ctx):
    """Reload the bot's commands"""
    await load_cogs()
    await ctx.send('Commands reloaded!')

if __name__ == '__main__':
    # Get token from environment variable
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN environment variable not found!")
        exit(1)
    
    bot.run(token)
