import discord
from discord.ext import commands
from discord.app_commands import AppCommandContext
import os

# Bot configuration
intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents, allowed_contexts=AppCommandContext(guild=True, dm_channel=False, private_channel=False))

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')

@bot.command(name='ping')
async def ping(ctx):
    """Check if the bot is responsive"""
    await ctx.send('Pong!')

@bot.command(name='hello')
async def hello(ctx):
    """Say hello to the user"""
    await ctx.send(f'Hello {ctx.author.mention}!')

if __name__ == '__main__':
    # Get token from environment variable
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN environment variable not found!")
        exit(1)
    
    bot.run(token)
