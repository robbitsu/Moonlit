import os
import httpx
from discord.ext import commands


API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8123")


class TestAPI(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="api_root", description="Call API root '/' and show response")
    async def api_root(self, ctx: commands.Context):
        url = f"{API_BASE_URL}/"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(url)
                r.raise_for_status()
                await ctx.reply(f"GET {url} -> {r.status_code} {r.json()}")
        except Exception as e:
            await ctx.reply(f"Request to {url} failed: {e}")

    @commands.hybrid_command(name="api_health", description="Call API '/health' and show status")
    async def api_health(self, ctx: commands.Context):
        url = f"{API_BASE_URL}/health"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(url)
                r.raise_for_status()
                data = r.json()
                await ctx.reply(f"GET {url} -> {r.status_code} status={data.get('status')} time={data.get('time')}")
        except Exception as e:
            await ctx.reply(f"Request to {url} failed: {e}")

    # Send custom request to API
    @commands.hybrid_command(name="api_request", description="Send a custom request to the API")
    async def api_request(self, ctx: commands.Context, url: str, method: str = "GET", body: str = None):
        if method not in ["GET", "POST", "DELETE"]:
            await ctx.reply(f"Invalid method: {method}")
            return
        if body and method != "POST":
            await ctx.reply(f"Body can only be used with POST method")
            return
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.request(method, url, json=body)
                r.raise_for_status()
                await ctx.reply(f"{method} {url} -> {r.status_code} {r.json()}")
        except Exception as e:
            await ctx.reply(f"Request to {url} failed: {e}")


async def setup(bot: commands.Bot):
    # If bot.production is True, throw an error
    if bot.production:
        raise Exception("TestAPI cog is not available in production")
    await bot.add_cog(TestAPI(bot))


