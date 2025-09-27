import os
import datetime
import discord
import ephem
from discord.ext import commands, tasks
from discord import app_commands


PHASE_IMAGE_MAP = {
    "new": "new_moon.png",
    "waxing_crescent": "waxing_crescent.png",
    "first_quarter": "first_quarter.png",
    "waxing_gibbous": "waxing_gibbous.png",
    "full": "full_moon.png",
    "waning_gibbous": "waning_gibbous.png",
    "third_quarter": "third_quarter.png",
    "waning_crescent": "waning_crescent.png",
}


def get_current_moon_phase_key(now: ephem.Date | None = None) -> str:
    """Return one of 8 phase keys matching available images.

    Keys: new, waxing_crescent, first_quarter, waxing_gibbous,
          full, waning_gibbous, third_quarter, waning_crescent
    """
    if now is None:
        now = ephem.now()

    # Compute nearest principal phase times
    prev_new = ephem.previous_new_moon(now)
    next_new = ephem.next_new_moon(now)
    prev_first = ephem.previous_first_quarter_moon(now)
    next_first = ephem.next_first_quarter_moon(now)
    prev_full = ephem.previous_full_moon(now)
    next_full = ephem.next_full_moon(now)
    prev_last = ephem.previous_last_quarter_moon(now)
    next_last = ephem.next_last_quarter_moon(now)

    # If we are close to a principal phase, snap to it
    tolerance_days = 0.75  # ~18 hours
    distances = {
        "new": abs(now - prev_new) if prev_new < now else abs(next_new - now),
        "first_quarter": abs(now - prev_first) if prev_first < now else abs(next_first - now),
        "full": abs(now - prev_full) if prev_full < now else abs(next_full - now),
        "third_quarter": abs(now - prev_last) if prev_last < now else abs(next_last - now),
    }
    nearest_key = min(distances, key=distances.get)
    if distances[nearest_key] <= tolerance_days:
        return nearest_key

    # Otherwise determine waxing/waning interval
    if prev_new < now < next_first:
        return "waxing_crescent"
    if prev_first < now < next_full:
        return "waxing_gibbous"
    if prev_full < now < next_last:
        return "waning_gibbous"
    if prev_last < now < next_new:
        return "waning_crescent"

    # Fallback using illumination and a small time delta to infer waxing/waning
    moon_now = ephem.Moon(now)
    illum_now = float(moon_now.phase)  # percent illuminated [0..100]
    moon_future = ephem.Moon(now + 0.5)  # 12 hours later
    illum_future = float(moon_future.phase)
    if illum_now < 1.0:
        return "new"
    if illum_now > 99.0:
        return "full"
    if illum_future > illum_now:
        # Waxing
        return "waxing_gibbous" if illum_now > 50.0 else "waxing_crescent"
    else:
        # Waning
        return "waning_gibbous" if illum_now > 50.0 else "waning_crescent"

class Moon(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._pfp_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pfp"))
        self.bot.moon_phase = get_current_moon_phase_key()

    async def update_moon_avatar(self) -> tuple[str, str]:
        """Compute current moon phase and update bot avatar.

        Returns (phase_key, image_name) on success. Raises on failure.
        """
        phase_key = get_current_moon_phase_key()
        image_name = PHASE_IMAGE_MAP[phase_key]
        image_path = os.path.join(self._pfp_dir, image_name)

        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"Moon avatar image not found: {image_path}")

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        self.bot.moon_phase = phase_key

        await self.bot.user.edit(avatar=image_bytes)
        return phase_key, image_name

    @commands.hybrid_command(name="update_moon", description="Update bot avatar to current moon phase")
    async def update_moon(self, ctx: commands.Context):
        """Slash/Prefix command to update the bot's avatar to the current moon phase."""
        # Check if the user is the owner
        if ctx.author.id != self.bot.owner_id:
            await ctx.reply("You are not the owner of the bot.", ephemeral=True)
            return

        try:
            phase_key, image_name = await self.update_moon_avatar()
            message = f"Updated avatar to phase: {phase_key} (image: {image_name})"
            if getattr(ctx, "interaction", None) is not None:
                await ctx.reply(message, ephemeral=True)
            else:
                await ctx.reply(message)
        except Exception as e:
            error_message = f"Failed to update moon avatar: {e}"
            if getattr(ctx, "interaction", None) is not None:
                await ctx.reply(error_message, ephemeral=True)
            else:
                await ctx.reply(error_message)

    @tasks.loop(time=datetime.time(hour=0, minute=0, tzinfo=datetime.timezone.utc))
    async def daily_update(self):
        try:
            phase_key, image_name = await self.update_moon_avatar()
            print(f"[Daily] Updated bot avatar to phase: {phase_key} -> {image_name}")
        except Exception as e:
            print(f"[Daily] Failed to update moon avatar: {e}")

    @daily_update.before_loop
    async def before_daily_update(self):
        await self.bot.wait_until_ready()

    async def cog_load(self):
        # Start daily scheduled task when cog loads
        if not self.daily_update.is_running():
            self.daily_update.start()

    async def cog_unload(self):
        if self.daily_update.is_running():
            self.daily_update.cancel()

async def setup(bot):
    await bot.add_cog(Moon(bot))
